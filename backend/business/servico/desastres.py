from uuid import UUID

from sqlalchemy.orm import Session

from business.servico.capacidades import CatalogoCapacidadeService
from business.servico.qualificacoes import auditar
from business.servico.recursos import referencia
from business.view_models.desastres import (
    AreaAfetadaInput,
    AreaAfetadaVM,
    AvaliacaoAreaInput,
    ClassificacaoInput,
    DesastreInput,
    DesastreTipoVM,
    DesastreVM,
    TipoDesastreInput,
    TipoDesastreVM,
)
from core.entity.cadastros import Instituicao, agora_utc
from core.entity.desastres import (
    AreaAfetada,
    Desastre,
    DesastreTipo,
    SituacaoDesastre,
    TipoDesastre,
)
from core.http.contratos import ErroNegocio
from infra.configurations.cadastros import instituicoes
from infra.configurations.desastres import areas_afetadas, desastres, tipos_desastre
from infra.database.desastres import TerritorioRepositorio


class TipoDesastreService(
    CatalogoCapacidadeService[TipoDesastre, TipoDesastreInput, TipoDesastreVM]
):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, TipoDesastre, tipos_desastre, TipoDesastreVM)

    def construir(self, dados: TipoDesastreInput, sujeito: str) -> TipoDesastre:
        return TipoDesastre(
            codigo=dados.codigo,
            nome=dados.nome,
            descricao=dados.descricao,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: TipoDesastre, dados: TipoDesastreInput) -> None:
        entidade.nome, entidade.descricao = dados.nome, dados.descricao


class DesastreService:
    def __init__(self, sessao: Session) -> None:
        self.sessao: Session = sessao
        self.repo: TerritorioRepositorio[Desastre] = TerritorioRepositorio(
            sessao, Desastre, desastres
        )

    def exigir(
        self, identificador: UUID, historico: bool = False, bloquear: bool = False
    ) -> Desastre:
        entidade: Desastre | None = self.repo.obter(identificador, historico, bloquear)
        if entidade is None:
            raise ErroNegocio(
                404, "Ocorrência não encontrada", "Ocorrência inexistente ou inativada."
            )
        return entidade

    def visualizar(self, entidade: Desastre, historico: bool = False) -> DesastreVM:
        vm: DesastreVM = DesastreVM.model_validate(entidade)
        coordenadora = referencia(
            self.sessao,
            Instituicao,
            instituicoes,
            entidade.id_instituicao_coordenadora,
            True,
            False,
        )
        vm.coordenadora_nome, vm.coordenadora_inativa = (
            coordenadora.nome,
            coordenadora.inativado_em is not None,
        )
        for classificacao in self.repo.classificacoes(entidade.id, historico):
            tipo = referencia(
                self.sessao,
                TipoDesastre,
                tipos_desastre,
                classificacao.id_tipo_desastre,
                True,
                False,
            )
            item: DesastreTipoVM = DesastreTipoVM.model_validate(classificacao)
            item.tipo_nome, item.tipo_inativo = tipo.nome, tipo.inativado_em is not None
            vm.classificacoes.append(item)
        return vm

    def listar(
        self, limite: int, deslocamento: int, busca: str | None, historico: bool
    ) -> list[DesastreVM]:
        return [
            self.visualizar(e, historico)
            for e in self.repo.listar(limite, deslocamento, busca, historico)
        ]

    def obter(self, identificador: UUID, historico: bool = False) -> DesastreVM:
        return self.visualizar(self.exigir(identificador, historico), historico)

    def classificar(
        self, entidade: Desastre, dados: list[ClassificacaoInput], sujeito: str
    ) -> None:
        # Todas as operações do agregado usam o bloqueio exclusivo da ocorrência.
        # Referências em ordem estável evitam inversões entre cadastros concorrentes.
        for item in sorted(dados, key=lambda c: c.id_tipo_desastre):
            referencia(self.sessao, TipoDesastre, tipos_desastre, item.id_tipo_desastre)
        anteriores: list[DesastreTipo] = self.repo.classificacoes(entidade.id)
        vigentes: dict[UUID, DesastreTipo] = {c.id_tipo_desastre: c for c in anteriores}
        ids: set[UUID] = {c.id_tipo_desastre for c in dados}
        for anterior in anteriores:
            if anterior.id_tipo_desastre not in ids:
                auditar(anterior, sujeito)
                anterior.inativado_em = anterior.atualizado_em
            elif anterior.principal:
                anterior.principal = False
        # Libera a unicidade parcial antes da promoção de outro principal.
        self.sessao.flush()
        for item in dados:
            atual: DesastreTipo | None = vigentes.get(item.id_tipo_desastre)
            if atual is None:
                atual = DesastreTipo(
                    id_desastre=entidade.id,
                    id_tipo_desastre=item.id_tipo_desastre,
                    principal=item.principal,
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
                self.sessao.add(atual)
            else:
                atual.principal = item.principal
                auditar(atual, sujeito)
        self.sessao.flush()

    def alterar(self, identificador: UUID | None, dados: DesastreInput, sujeito: str) -> DesastreVM:
        with self.sessao.begin():
            if identificador is None:
                entidade: Desastre = Desastre(
                    titulo=dados.titulo,
                    descricao=dados.descricao,
                    inicio_em=dados.inicio_em,
                    situacao=dados.situacao,
                    id_instituicao_coordenadora=dados.id_instituicao_coordenadora,
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
            else:
                entidade = self.exigir(identificador, bloquear=True)
                if (
                    entidade.situacao == SituacaoDesastre.ENCERRADO
                    and dados.situacao != SituacaoDesastre.ENCERRADO
                ):
                    raise ErroNegocio(
                        409,
                        "Ocorrência encerrada",
                        "Reabertura operacional não está disponível neste incremento.",
                    )
                auditar(entidade, sujeito)
            referencia(self.sessao, Instituicao, instituicoes, dados.id_instituicao_coordenadora)
            entidade.titulo, entidade.descricao = dados.titulo, dados.descricao
            entidade.inicio_em, entidade.encerramento_em = dados.inicio_em, dados.encerramento_em
            entidade.situacao = dados.situacao
            entidade.id_instituicao_coordenadora = dados.id_instituicao_coordenadora
            self.sessao.add(entidade)
            self.sessao.flush()
            self.classificar(entidade, dados.classificacoes, sujeito)
            resultado: DesastreVM = self.visualizar(entidade)
        return resultado

    def criar(self, dados: DesastreInput, sujeito: str) -> DesastreVM:
        return self.alterar(None, dados, sujeito)

    def editar(self, identificador: UUID, dados: DesastreInput, sujeito: str) -> DesastreVM:
        return self.alterar(identificador, dados, sujeito)

    def inativar(self, identificador: UUID, sujeito: str) -> DesastreVM:
        with self.sessao.begin():
            entidade: Desastre = self.exigir(identificador, bloquear=True)
            auditar(entidade, sujeito)
            entidade.inativado_em = entidade.atualizado_em
            self.sessao.flush()
            resultado: DesastreVM = self.visualizar(entidade, True)
        return resultado


class AreaAfetadaService:
    def __init__(self, sessao: Session, id_desastre: UUID) -> None:
        self.sessao: Session = sessao
        self.id_desastre: UUID = id_desastre
        self.desastres: DesastreService = DesastreService(sessao)
        self.repo: TerritorioRepositorio[AreaAfetada] = TerritorioRepositorio(
            sessao, AreaAfetada, areas_afetadas, id_desastre
        )

    def exigir(
        self, identificador: UUID, historico: bool = False, bloquear: bool = False
    ) -> AreaAfetada:
        area: AreaAfetada | None = self.repo.obter(identificador, historico, bloquear)
        if area is None:
            raise ErroNegocio(
                404, "Área não encontrada", "Área inexistente ou não pertence à ocorrência."
            )
        return area

    def listar(
        self, limite: int, deslocamento: int, busca: str | None, historico: bool
    ) -> list[AreaAfetadaVM]:
        self.desastres.exigir(self.id_desastre, historico)
        return [
            AreaAfetadaVM.model_validate(a)
            for a in self.repo.listar(limite, deslocamento, busca, historico)
        ]

    def obter(self, identificador: UUID, historico: bool = False) -> AreaAfetadaVM:
        self.desastres.exigir(self.id_desastre, historico)
        return AreaAfetadaVM.model_validate(self.exigir(identificador, historico))

    def alterar(
        self, identificador: UUID | None, dados: AreaAfetadaInput, sujeito: str
    ) -> AreaAfetadaVM:
        with self.sessao.begin():
            self.desastres.exigir(self.id_desastre, bloquear=True)
            if identificador is None:
                area: AreaAfetada = AreaAfetada(
                    id_desastre=self.id_desastre,
                    nome=dados.nome,
                    descricao=dados.descricao,
                    municipio_codigo_ibge=dados.municipio_codigo_ibge,
                    geometria=dados.geometria.para_entidade(),
                    gravidade=dados.gravidade,
                    situacao=dados.situacao,
                    ultima_avaliacao_em=agora_utc(),
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
                self.sessao.add(area)
            else:
                area = self.exigir(identificador, bloquear=True)
                if area.gravidade != dados.gravidade or area.situacao != dados.situacao:
                    area.ultima_avaliacao_em = agora_utc()
                auditar(area, sujeito)
            area.nome, area.descricao = dados.nome, dados.descricao
            area.municipio_codigo_ibge, area.geometria = (
                dados.municipio_codigo_ibge,
                dados.geometria.para_entidade(),
            )
            area.gravidade, area.situacao = dados.gravidade, dados.situacao
            self.sessao.flush()
            resultado: AreaAfetadaVM = AreaAfetadaVM.model_validate(area)
        return resultado

    def avaliar(
        self, identificador: UUID, dados: AvaliacaoAreaInput, sujeito: str
    ) -> AreaAfetadaVM:
        with self.sessao.begin():
            self.desastres.exigir(self.id_desastre, bloquear=True)
            area: AreaAfetada = self.exigir(identificador, bloquear=True)
            area.gravidade, area.situacao = dados.gravidade, dados.situacao
            area.ultima_avaliacao_em = agora_utc()
            auditar(area, sujeito)
            self.sessao.flush()
            resultado: AreaAfetadaVM = AreaAfetadaVM.model_validate(area)
        return resultado

    def criar(self, dados: AreaAfetadaInput, sujeito: str) -> AreaAfetadaVM:
        return self.alterar(None, dados, sujeito)

    def editar(self, identificador: UUID, dados: AreaAfetadaInput, sujeito: str) -> AreaAfetadaVM:
        return self.alterar(identificador, dados, sujeito)

    def inativar(self, identificador: UUID, sujeito: str) -> AreaAfetadaVM:
        with self.sessao.begin():
            self.desastres.exigir(self.id_desastre, historico=True, bloquear=True)
            area: AreaAfetada = self.exigir(identificador, bloquear=True)
            auditar(area, sujeito)
            area.inativado_em = area.atualizado_em
            self.sessao.flush()
            resultado: AreaAfetadaVM = AreaAfetadaVM.model_validate(area)
        return resultado

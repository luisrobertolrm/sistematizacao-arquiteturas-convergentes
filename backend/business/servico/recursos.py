from uuid import UUID

from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from business.servico.qualificacoes import auditar
from business.view_models.cadastros import AuditoriaVM
from business.view_models.qualificacoes import Entrada
from business.view_models.recursos import (
    OfertaAtividadeInput,
    OfertaAtividadeVM,
    OfertaRecursoInput,
    OfertaRecursoVM,
    RecursoInput,
    RecursoVM,
    ResponsavelInput,
    ResponsavelVM,
    TipoRecursoInput,
    TipoRecursoVM,
)
from core.entity.cadastros import Entidade, Instituicao, Pessoa, agora_utc
from core.entity.capacidades import Atividade, UnidadeMedida
from core.entity.qualificacoes import SituacaoValidacao
from core.entity.recursos import (
    ModoControleRecurso,
    OfertaAtividade,
    OfertaAtividadeRecurso,
    Recurso,
    Responsavel,
    TipoRecurso,
)
from core.http.contratos import ErroNegocio
from core.semantica import hash_tipo_recurso
from infra.configurations.cadastros import instituicoes, pessoas
from infra.configurations.capacidades import atividades, unidades_medida
from infra.configurations.recursos import (
    oferta_atividade_recurso,
    ofertas_atividade,
    recursos,
    tipos_recurso,
)
from infra.database.recursos import RecursosRepositorio


def referencia[T: Entidade](
    sessao: Session,
    tipo: type[T],
    tabela: Table,
    identificador: UUID,
    historico: bool = False,
    bloquear: bool = True,
) -> T:
    entidade: T | None = RecursosRepositorio(sessao, tipo, tabela).obter(
        identificador,
        historico,
        compartilhado=bloquear,
    )
    if entidade is None:
        raise ErroNegocio(404, "Referência não encontrada", "Escolha uma referência ativa.")
    return entidade


def preencher_responsavel(sessao: Session, entidade: Responsavel, dados: ResponsavelInput) -> None:
    if dados.instituicao_id is not None:
        referencia(sessao, Instituicao, instituicoes, dados.instituicao_id)
    elif dados.pessoa_id is not None:
        referencia(sessao, Pessoa, pessoas, dados.pessoa_id)
    entidade.instituicao_id, entidade.pessoa_id = dados.instituicao_id, dados.pessoa_id


def visualizar_responsavel(sessao: Session, entidade: Responsavel, vm: ResponsavelVM) -> None:
    dono: Instituicao | Pessoa
    if entidade.instituicao_id is not None:
        dono = referencia(sessao, Instituicao, instituicoes, entidade.instituicao_id, True, False)
    elif entidade.pessoa_id is not None:
        dono = referencia(sessao, Pessoa, pessoas, entidade.pessoa_id, True, False)
    else:
        raise ValueError("Responsável ausente em registro persistido.")
    vm.responsavel_nome = dono.nome
    vm.responsavel_inativo = dono.inativado_em is not None


class RecursosService[T: Entidade, I: Entrada, V: AuditoriaVM]:
    def __init__(self, sessao: Session, tipo: type[T], tabela: Table, vm: type[V]) -> None:
        self.sessao: Session = sessao
        self.repo: RecursosRepositorio[T] = RecursosRepositorio(sessao, tipo, tabela)
        self.vm: type[V] = vm

    def guardar(self, historico: bool, escrita: bool = False) -> None:
        pass

    def exigir(self, identificador: UUID, historico: bool = False, bloquear: bool = False) -> T:
        entidade: T | None = self.repo.obter(identificador, historico, bloquear)
        if entidade is None:
            raise ErroNegocio(404, "Cadastro não encontrado", "Cadastro inexistente ou inativo.")
        return entidade

    def visualizar(self, entidade: T) -> V:
        return self.vm.model_validate(entidade)

    def listar(self, limite: int, deslocamento: int, busca: str | None, historico: bool) -> list[V]:
        self.guardar(historico)
        return [
            self.visualizar(e) for e in self.repo.listar(limite, deslocamento, busca, historico)
        ]

    def obter(self, identificador: UUID, historico: bool = False) -> V:
        self.guardar(historico)
        return self.visualizar(self.exigir(identificador, historico))

    def construir(self, dados: I, sujeito: str) -> T:
        raise NotImplementedError

    def preencher(self, entidade: T, dados: I, nova: bool) -> None:
        raise NotImplementedError

    def criar(self, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            self.guardar(False, True)
            entidade: T = self.construir(dados, sujeito)
            self.preencher(entidade, dados, True)
            self.sessao.add(entidade)
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado

    def editar(self, identificador: UUID, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            self.guardar(False, True)
            entidade: T = self.exigir(identificador, bloquear=True)
            self.preencher(entidade, dados, False)
            auditar(entidade, sujeito)
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado

    def inativar(self, identificador: UUID, sujeito: str) -> V:
        with self.sessao.begin():
            self.guardar(True, True)
            entidade: T = self.exigir(identificador, bloquear=True)
            auditar(entidade, sujeito)
            entidade.inativado_em = entidade.atualizado_em
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado


class TipoRecursoService(RecursosService[TipoRecurso, TipoRecursoInput, TipoRecursoVM]):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, TipoRecurso, tipos_recurso, TipoRecursoVM)

    def construir(self, dados: TipoRecursoInput, sujeito: str) -> TipoRecurso:
        return TipoRecurso(
            nome=dados.nome,
            categoria=dados.categoria,
            id_unidade_medida=dados.id_unidade_medida,
            modo_controle=dados.modo_controle,
            hash_conteudo_semantico="",
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: TipoRecurso, dados: TipoRecursoInput, nova: bool) -> None:
        if (
            not nova
            and (
                entidade.id_unidade_medida != dados.id_unidade_medida
                or entidade.modo_controle != dados.modo_controle
            )
            and self.sessao.scalar(
                select(recursos.c.id).where(recursos.c.tipo_recurso_id == entidade.id).limit(1)
            )
            is not None
        ):
            raise ErroNegocio(
                409,
                "Tipo utilizado",
                "Unidade e modo de controle de um tipo utilizado são estáveis.",
            )
        referencia(self.sessao, UnidadeMedida, unidades_medida, dados.id_unidade_medida)
        entidade.nome, entidade.descricao = dados.nome, dados.descricao
        entidade.categoria = dados.categoria
        entidade.id_unidade_medida, entidade.modo_controle = (
            dados.id_unidade_medida,
            dados.modo_controle,
        )
        entidade.hash_conteudo_semantico = hash_tipo_recurso(entidade)

    def visualizar(self, entidade: TipoRecurso) -> TipoRecursoVM:
        vm: TipoRecursoVM = super().visualizar(entidade)
        unidade = referencia(
            self.sessao, UnidadeMedida, unidades_medida, entidade.id_unidade_medida, True, False
        )
        vm.unidade_nome, vm.unidade_simbolo = unidade.nome, unidade.simbolo
        vm.unidade_inativa = unidade.inativado_em is not None
        return vm


class RecursoService(RecursosService[Recurso, RecursoInput, RecursoVM]):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, Recurso, recursos, RecursoVM)

    def construir(self, dados: RecursoInput, sujeito: str) -> Recurso:
        return Recurso(
            tipo_recurso_id=dados.tipo_recurso_id,
            nome=dados.nome,
            quantidade_total=dados.quantidade_total,
            municipio_codigo_ibge=dados.municipio_codigo_ibge,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: Recurso, dados: RecursoInput, nova: bool) -> None:
        if not nova and entidade.tipo_recurso_id != dados.tipo_recurso_id:
            raise ErroNegocio(
                409,
                "Tipo estável",
                "Crie outro recurso para mudar seu tipo e preservar o histórico.",
            )
        tipo = referencia(self.sessao, TipoRecurso, tipos_recurso, dados.tipo_recurso_id)
        referencia(self.sessao, UnidadeMedida, unidades_medida, tipo.id_unidade_medida)
        if tipo.modo_controle == ModoControleRecurso.INDIVIDUAL and dados.quantidade_total != 1:
            raise ErroNegocio(
                422,
                "Quantidade individual",
                "Um recurso individual deve ter quantidade total igual a 1.",
            )
        preencher_responsavel(self.sessao, entidade, dados)
        entidade.nome, entidade.descricao = dados.nome, dados.descricao
        entidade.identificacao = dados.identificacao
        entidade.quantidade_total, entidade.estado_operacional = (
            dados.quantidade_total,
            dados.estado_operacional,
        )
        entidade.municipio_codigo_ibge = dados.municipio_codigo_ibge
        entidade.latitude, entidade.longitude = dados.latitude, dados.longitude

    def visualizar(self, entidade: Recurso) -> RecursoVM:
        tipo = referencia(
            self.sessao, TipoRecurso, tipos_recurso, entidade.tipo_recurso_id, True, False
        )
        vm: RecursoVM = RecursoVM.model_validate(entidade)
        vm.tipo_recurso_nome, vm.modo_controle = tipo.nome, tipo.modo_controle
        vm.tipo_recurso_inativo = tipo.inativado_em is not None
        unidade = referencia(
            self.sessao, UnidadeMedida, unidades_medida, tipo.id_unidade_medida, True, False
        )
        vm.unidade_nome, vm.unidade_simbolo = unidade.nome, unidade.simbolo
        vm.unidade_inativa = unidade.inativado_em is not None
        visualizar_responsavel(self.sessao, entidade, vm)
        return vm


class OfertaAtividadeService(
    RecursosService[OfertaAtividade, OfertaAtividadeInput, OfertaAtividadeVM]
):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, OfertaAtividade, ofertas_atividade, OfertaAtividadeVM)

    def construir(self, dados: OfertaAtividadeInput, sujeito: str) -> OfertaAtividade:
        return OfertaAtividade(
            atividade_id=dados.atividade_id,
            municipio_atendimento_codigo_ibge=dados.municipio_atendimento_codigo_ibge,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: OfertaAtividade, dados: OfertaAtividadeInput, nova: bool) -> None:
        if not nova and entidade.atividade_id != dados.atividade_id:
            raise ErroNegocio(
                409,
                "Atividade estável",
                "Crie outra oferta para mudar sua atividade e preservar o histórico.",
            )
        atividade = referencia(self.sessao, Atividade, atividades, dados.atividade_id)
        if dados.capacidade_declarada is not None:
            if atividade.id_unidade_capacidade is None:
                raise ErroNegocio(
                    422,
                    "Capacidade sem unidade",
                    "A atividade precisa de unidade para declarar capacidade.",
                )
            referencia(self.sessao, UnidadeMedida, unidades_medida, atividade.id_unidade_capacidade)
        preencher_responsavel(self.sessao, entidade, dados)
        entidade.municipio_atendimento_codigo_ibge = dados.municipio_atendimento_codigo_ibge
        entidade.descricao_complementar, entidade.capacidade_declarada = (
            dados.descricao_complementar,
            dados.capacidade_declarada,
        )
        # A data representa a validação da versão atual da oferta.
        entidade.situacao_validacao = dados.situacao_validacao
        entidade.validado_em = (
            agora_utc() if dados.situacao_validacao == SituacaoValidacao.VALIDADA else None
        )

    def visualizar(self, entidade: OfertaAtividade) -> OfertaAtividadeVM:
        vm: OfertaAtividadeVM = super().visualizar(entidade)
        atividade = referencia(
            self.sessao, Atividade, atividades, entidade.atividade_id, True, False
        )
        vm.atividade_nome, vm.atividade_inativa = atividade.nome, atividade.inativado_em is not None
        if atividade.id_unidade_capacidade is not None:
            unidade = referencia(
                self.sessao,
                UnidadeMedida,
                unidades_medida,
                atividade.id_unidade_capacidade,
                True,
                False,
            )
            vm.unidade_nome, vm.unidade_inativa = unidade.nome, unidade.inativado_em is not None
        visualizar_responsavel(self.sessao, entidade, vm)
        return vm


class OfertaRecursoService(
    RecursosService[OfertaAtividadeRecurso, OfertaRecursoInput, OfertaRecursoVM]
):
    def __init__(self, sessao: Session, oferta_id: UUID) -> None:
        super().__init__(sessao, OfertaAtividadeRecurso, oferta_atividade_recurso, OfertaRecursoVM)
        self.oferta_id: UUID = oferta_id
        self.repo = RecursosRepositorio(
            sessao, OfertaAtividadeRecurso, oferta_atividade_recurso, oferta_id
        )

    def guardar(self, historico: bool, escrita: bool = False) -> None:
        pai = RecursosRepositorio(self.sessao, OfertaAtividade, ofertas_atividade).obter(
            self.oferta_id,
            historico,
            bloquear=escrita,
        )
        if pai is None:
            raise ErroNegocio(404, "Oferta não encontrada", "Oferta inexistente ou inativa.")

    def construir(self, dados: OfertaRecursoInput, sujeito: str) -> OfertaAtividadeRecurso:
        return OfertaAtividadeRecurso(
            oferta_atividade_id=self.oferta_id,
            recurso_id=dados.recurso_id,
            quantidade_prevista=dados.quantidade_prevista,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(
        self, entidade: OfertaAtividadeRecurso, dados: OfertaRecursoInput, nova: bool
    ) -> None:
        if not nova and entidade.recurso_id != dados.recurso_id:
            raise ErroNegocio(
                409, "Recurso estável", "Inative o vínculo e crie outro para mudar o recurso."
            )
        recurso = referencia(self.sessao, Recurso, recursos, dados.recurso_id)
        tipo = referencia(self.sessao, TipoRecurso, tipos_recurso, recurso.tipo_recurso_id)
        referencia(self.sessao, UnidadeMedida, unidades_medida, tipo.id_unidade_medida)
        if tipo.modo_controle == ModoControleRecurso.INDIVIDUAL and dados.quantidade_prevista != 1:
            raise ErroNegocio(
                422,
                "Quantidade individual",
                "Um vínculo de recurso individual deve prever quantidade 1.",
            )
        entidade.quantidade_prevista = dados.quantidade_prevista

    def visualizar(self, entidade: OfertaAtividadeRecurso) -> OfertaRecursoVM:
        vm: OfertaRecursoVM = super().visualizar(entidade)
        recurso = RecursoService(self.sessao).obter(entidade.recurso_id, True)
        vm.recurso_nome, vm.recurso_inativo = recurso.nome, recurso.inativado_em is not None
        vm.recurso_estado, vm.recurso_responsavel_nome = (
            recurso.estado_operacional,
            recurso.responsavel_nome,
        )
        vm.unidade_simbolo = recurso.unidade_simbolo
        return vm

from uuid import UUID

from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from business.servico.qualificacoes import auditar
from business.view_models.cadastros import AuditoriaVM
from business.view_models.capacidades import (
    AtividadeInput,
    AtividadeTermoInput,
    AtividadeTermoVM,
    AtividadeVM,
    CatalogoCodigoInput,
    CategoriaAtividadeInput,
    CategoriaAtividadeVM,
    UnidadeMedidaInput,
    UnidadeMedidaVM,
)
from core.entity.capacidades import (
    Atividade,
    AtividadeTermo,
    CatalogoComCodigo,
    CategoriaAtividade,
    UnidadeMedida,
)
from core.http.contratos import ErroNegocio
from core.semantica import hash_atividade
from infra.configurations.capacidades import atividades, categorias_atividade, unidades_medida
from infra.configurations.recursos import ofertas_atividade
from infra.database.capacidades import CatalogoCapacidadeRepositorio, TermosRepositorio


class CatalogoCapacidadeService[T: CatalogoComCodigo, I: CatalogoCodigoInput, V: AuditoriaVM]:
    def __init__(self, sessao: Session, tipo: type[T], tabela: Table, vm: type[V]) -> None:
        self.sessao: Session = sessao
        self.repo: CatalogoCapacidadeRepositorio[T] = CatalogoCapacidadeRepositorio(
            sessao, tipo, tabela
        )
        self.vm: type[V] = vm

    def exigir(self, identificador: UUID, historico: bool = False, bloquear: bool = False) -> T:
        entidade: T | None = self.repo.obter(identificador, historico, bloquear)
        if entidade is None:
            raise ErroNegocio(404, "Cadastro não encontrado", "Cadastro inexistente ou inativo.")
        return entidade

    def visualizar(self, entidade: T) -> V:
        return self.vm.model_validate(entidade)

    def listar(
        self,
        limite: int,
        deslocamento: int,
        busca: str | None,
        incluir_inativos: bool,
    ) -> list[V]:
        return [
            self.visualizar(e)
            for e in self.repo.listar(limite, deslocamento, busca, incluir_inativos)
        ]

    def obter(self, identificador: UUID, incluir_inativos: bool = False) -> V:
        return self.visualizar(self.exigir(identificador, incluir_inativos))

    def construir(self, dados: I, sujeito: str) -> T:
        raise NotImplementedError

    def preencher(self, entidade: T, dados: I) -> None:
        raise NotImplementedError

    def preparar(self, entidade: T) -> None:
        pass

    def criar(self, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            entidade: T = self.construir(dados, sujeito)
            self.preencher(entidade, dados)
            self.preparar(entidade)
            self.sessao.add(entidade)
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado

    def editar(self, identificador: UUID, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            entidade: T = self.exigir(identificador, bloquear=True)
            if entidade.codigo != dados.codigo:
                raise ErroNegocio(
                    409, "Código estável", "O código não pode ser alterado após criar."
                )
            self.preencher(entidade, dados)
            self.preparar(entidade)
            auditar(entidade, sujeito)
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado

    def inativar(self, identificador: UUID, sujeito: str) -> V:
        with self.sessao.begin():
            entidade: T = self.exigir(identificador, bloquear=True)
            auditar(entidade, sujeito)
            entidade.inativado_em = entidade.atualizado_em
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado


class UnidadeMedidaService(
    CatalogoCapacidadeService[UnidadeMedida, UnidadeMedidaInput, UnidadeMedidaVM]
):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, UnidadeMedida, unidades_medida, UnidadeMedidaVM)

    def construir(self, dados: UnidadeMedidaInput, sujeito: str) -> UnidadeMedida:
        return UnidadeMedida(
            codigo=dados.codigo,
            nome=dados.nome,
            simbolo=dados.simbolo,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: UnidadeMedida, dados: UnidadeMedidaInput) -> None:
        entidade.nome, entidade.simbolo = dados.nome, dados.simbolo


class CategoriaAtividadeService(
    CatalogoCapacidadeService[CategoriaAtividade, CategoriaAtividadeInput, CategoriaAtividadeVM]
):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, CategoriaAtividade, categorias_atividade, CategoriaAtividadeVM)

    def construir(self, dados: CategoriaAtividadeInput, sujeito: str) -> CategoriaAtividade:
        return CategoriaAtividade(
            codigo=dados.codigo, nome=dados.nome, criado_por=sujeito, atualizado_por=sujeito
        )

    def preencher(self, entidade: CategoriaAtividade, dados: CategoriaAtividadeInput) -> None:
        entidade.nome, entidade.descricao = dados.nome, dados.descricao


class AtividadeService(CatalogoCapacidadeService[Atividade, AtividadeInput, AtividadeVM]):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, Atividade, atividades, AtividadeVM)
        self.termos: TermosRepositorio = TermosRepositorio(sessao)

    def visualizar(self, entidade: Atividade) -> AtividadeVM:
        resultado: AtividadeVM = self.vm.model_validate(entidade)
        categoria: CategoriaAtividade | None = self.sessao.get(
            CategoriaAtividade, entidade.categoria_id
        )
        unidade: UnidadeMedida | None = (
            self.sessao.get(UnidadeMedida, entidade.id_unidade_capacidade)
            if entidade.id_unidade_capacidade
            else None
        )
        if categoria is not None:
            resultado.categoria_nome = categoria.nome
            resultado.categoria_inativa = categoria.inativado_em is not None
        if unidade is not None:
            resultado.unidade_nome = unidade.nome
            resultado.unidade_inativa = unidade.inativado_em is not None
        return resultado

    def construir(self, dados: AtividadeInput, sujeito: str) -> Atividade:
        return Atividade(
            codigo=dados.codigo,
            nome=dados.nome,
            descricao=dados.descricao,
            categoria_id=dados.categoria_id,
            hash_conteudo_semantico="",
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: Atividade, dados: AtividadeInput) -> None:
        if (
            entidade.id_unidade_capacidade != dados.id_unidade_capacidade
            and self.sessao.scalar(
                select(ofertas_atividade.c.id)
                .where(
                    ofertas_atividade.c.atividade_id == entidade.id,
                    ofertas_atividade.c.capacidade_declarada.is_not(None),
                )
                .limit(1)
            )
            is not None
        ):
            raise ErroNegocio(
                409,
                "Unidade utilizada",
                "A unidade não pode mudar após declarar capacidade em uma oferta.",
            )
        categoria_repo = CatalogoCapacidadeRepositorio(
            self.sessao, CategoriaAtividade, categorias_atividade
        )
        # SHARE protege as referências até o commit, inclusive contra inativação concorrente.
        if categoria_repo.obter(dados.categoria_id, compartilhado=True) is None:
            raise ErroNegocio(404, "Categoria não encontrada", "Escolha uma categoria ativa.")
        if dados.id_unidade_capacidade is not None:
            unidade_repo = CatalogoCapacidadeRepositorio(
                self.sessao, UnidadeMedida, unidades_medida
            )
            if unidade_repo.obter(dados.id_unidade_capacidade, compartilhado=True) is None:
                raise ErroNegocio(404, "Unidade não encontrada", "Escolha uma unidade ativa.")
        entidade.nome, entidade.descricao = dados.nome, dados.descricao
        entidade.categoria_id = dados.categoria_id
        entidade.id_unidade_capacidade = dados.id_unidade_capacidade
        entidade.orientacoes, entidade.restricoes = dados.orientacoes, dados.restricoes

    def preparar(self, entidade: Atividade) -> None:
        # Entidade nova ainda não foi adicionada; consulta não provoca flush de hash vazio.
        entidade.hash_conteudo_semantico = hash_atividade(
            entidade, self.termos.textos_ativos(entidade.id)
        )


class AtividadeTermoService:
    def __init__(self, sessao: Session) -> None:
        self.sessao: Session = sessao
        self.atividades: AtividadeService = AtividadeService(sessao)
        self.repo: TermosRepositorio = TermosRepositorio(sessao)

    def exigir(
        self, atividade_id: UUID, identificador: UUID, historico: bool = False
    ) -> AtividadeTermo:
        termo: AtividadeTermo | None = self.repo.obter(atividade_id, identificador, historico)
        if termo is None:
            raise ErroNegocio(404, "Termo não encontrado", "Termo inexistente nesta atividade.")
        return termo

    def listar(
        self,
        atividade_id: UUID,
        limite: int,
        deslocamento: int,
        incluir_inativos: bool,
    ) -> list[AtividadeTermoVM]:
        self.atividades.exigir(atividade_id, incluir_inativos)
        return [
            AtividadeTermoVM.model_validate(t)
            for t in self.repo.listar(atividade_id, limite, deslocamento, incluir_inativos)
        ]

    def obter(
        self,
        atividade_id: UUID,
        identificador: UUID,
        incluir_inativos: bool,
    ) -> AtividadeTermoVM:
        self.atividades.exigir(atividade_id, incluir_inativos)
        return AtividadeTermoVM.model_validate(
            self.exigir(atividade_id, identificador, incluir_inativos)
        )

    def alterar(
        self,
        atividade_id: UUID,
        identificador: UUID | None,
        dados: AtividadeTermoInput | None,
        sujeito: str,
    ) -> AtividadeTermoVM:
        with self.sessao.begin():
            # A mesma linha serializa edição da atividade e todas as alterações de seus termos.
            atividade: Atividade = self.atividades.exigir(
                atividade_id, historico=dados is None, bloquear=True
            )
            if identificador is None:
                if dados is None:
                    raise ValueError("Novo termo exige dados.")
                termo: AtividadeTermo = AtividadeTermo(
                    atividade_id=atividade_id,
                    termo=dados.termo,
                    criado_por=sujeito,
                    atualizado_por=sujeito,
                )
                self.sessao.add(termo)
            else:
                termo = self.exigir(atividade_id, identificador)
                auditar(termo, sujeito)
                if dados is None:
                    termo.inativado_em = termo.atualizado_em
                else:
                    termo.termo = dados.termo
            self.sessao.flush()
            atividade.hash_conteudo_semantico = hash_atividade(
                atividade, self.repo.textos_ativos(atividade_id)
            )
            auditar(atividade, sujeito)
            self.sessao.flush()
            resultado: AtividadeTermoVM = AtividadeTermoVM.model_validate(termo)
        return resultado

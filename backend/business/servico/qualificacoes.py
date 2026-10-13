from uuid import UUID

from sqlalchemy import Table
from sqlalchemy.orm import Session

from business.view_models.qualificacoes import (
    CatalogoInput,
    CursoInput,
    CursoVM,
    PessoaCursoInput,
    PessoaCursoVM,
    PessoaInstituicaoInput,
    PessoaInstituicaoVM,
    PessoaProfissaoInput,
    PessoaProfissaoVM,
    ProfissaoInput,
    ProfissaoVM,
    VinculoInput,
    VinculoVM,
)
from core.entity.cadastros import Entidade, agora_utc
from core.entity.qualificacoes import (
    Curso,
    PessoaCurso,
    PessoaInstituicao,
    PessoaProfissao,
    Profissao,
    VinculoPessoa,
)
from core.http.contratos import ErroNegocio
from core.semantica import hash_qualificacao
from infra.configurations.cadastros import instituicoes
from infra.configurations.qualificacoes import (
    cursos,
    pessoa_curso,
    pessoa_instituicao,
    pessoa_profissao,
    profissoes,
)
from infra.database.repositorio import Repositorio
from infra.database.vinculos import VinculosRepositorio


def auditar(entidade: Entidade, sujeito: str) -> None:
    entidade.atualizado_em = agora_utc()
    entidade.atualizado_por = sujeito


class CatalogoService[T: (Profissao, Curso), I: CatalogoInput, V: (ProfissaoVM, CursoVM)]:
    def __init__(self, sessao: Session, tipo: type[T], tabela: Table, vm: type[V]) -> None:
        self.sessao: Session = sessao
        self.repo: Repositorio[T] = Repositorio(sessao, tipo, tabela)
        self.vm: type[V] = vm

    def listar(self, limite: int, deslocamento: int, busca: str | None = None) -> list[V]:
        return [self.vm.model_validate(e) for e in self.repo.listar(limite, deslocamento, busca)]

    def obter_entidade(self, identificador: UUID) -> T:
        entidade: T | None = self.repo.obter(identificador)
        if entidade is None:
            raise ErroNegocio(404, "Catálogo não encontrado", "Cadastro inexistente ou inativo.")
        return entidade

    def obter(self, identificador: UUID) -> V:
        return self.vm.model_validate(self.obter_entidade(identificador))

    def construir(self, dados: I, sujeito: str) -> T:
        raise NotImplementedError

    def preencher(self, entidade: T, dados: I) -> None:
        raise NotImplementedError

    def criar(self, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            entidade: T = self.construir(dados, sujeito)
            self.preencher(entidade, dados)
            entidade.hash_conteudo_semantico = hash_qualificacao(entidade)
            self.repo.adicionar(entidade)
            self.sessao.flush()
            resultado: V = self.vm.model_validate(entidade)
        return resultado

    def editar(self, identificador: UUID, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            entidade: T = self.obter_entidade(identificador)
            self.preencher(entidade, dados)
            entidade.hash_conteudo_semantico = hash_qualificacao(entidade)
            auditar(entidade, sujeito)
            self.sessao.flush()
            resultado: V = self.vm.model_validate(entidade)
        return resultado

    def inativar(self, identificador: UUID, sujeito: str) -> V:
        with self.sessao.begin():
            entidade: T = self.obter_entidade(identificador)
            auditar(entidade, sujeito)
            entidade.inativado_em = entidade.atualizado_em
            self.sessao.flush()
            resultado: V = self.vm.model_validate(entidade)
        return resultado


class ProfissaoService(CatalogoService[Profissao, ProfissaoInput, ProfissaoVM]):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, Profissao, profissoes, ProfissaoVM)

    def construir(self, dados: ProfissaoInput, sujeito: str) -> Profissao:
        return Profissao(
            nome=dados.nome, hash_conteudo_semantico="", criado_por=sujeito, atualizado_por=sujeito
        )

    def preencher(self, entidade: Profissao, dados: ProfissaoInput) -> None:
        entidade.nome = dados.nome
        entidade.descricao = dados.descricao
        entidade.codigo_cbo = dados.codigo_cbo


class CursoService(CatalogoService[Curso, CursoInput, CursoVM]):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, Curso, cursos, CursoVM)

    def construir(self, dados: CursoInput, sujeito: str) -> Curso:
        return Curso(
            nome=dados.nome,
            tipo=dados.tipo,
            hash_conteudo_semantico="",
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: Curso, dados: CursoInput) -> None:
        entidade.nome = dados.nome
        entidade.descricao = dados.descricao
        entidade.tipo = dados.tipo


class VinculoService[T: VinculoPessoa, I: VinculoInput, V: VinculoVM]:
    def __init__(
        self,
        sessao: Session,
        tipo: type[T],
        tabela: Table,
        referencia: Table,
        coluna: str,
        vm: type[V],
    ) -> None:
        self.sessao: Session = sessao
        self.repo: VinculosRepositorio[T] = VinculosRepositorio(
            sessao, tipo, tabela, referencia, coluna
        )
        self.vm: type[V] = vm

    def visualizar(self, entidade: T, nome: str | None = None) -> V:
        resultado: V = self.vm.model_validate(entidade)
        resultado.referencia_nome = (
            nome if nome is not None else self.repo.nome_referencia(entidade)
        )
        return resultado

    def listar(
        self, pessoa_id: UUID, limite: int, deslocamento: int, incluir_inativos: bool
    ) -> list[V]:
        self.repo.exigir_pessoa(pessoa_id, ativo=not incluir_inativos)
        return [
            self.visualizar(e, nome)
            for e, nome in self.repo.listar(pessoa_id, limite, deslocamento, incluir_inativos)
        ]

    def obter(self, pessoa_id: UUID, identificador: UUID, incluir_inativos: bool) -> V:
        self.repo.exigir_pessoa(pessoa_id, ativo=not incluir_inativos)
        entidade: T = self.repo.obter(pessoa_id, identificador, incluir_inativos)
        if not incluir_inativos:
            self.repo.exigir_registro(self.repo.referencia, entidade.id_referencia, True, False)
        return self.visualizar(entidade)

    def construir(self, pessoa_id: UUID, dados: I, sujeito: str) -> T:
        raise NotImplementedError

    def preencher(self, entidade: T, dados: I) -> None:
        raise NotImplementedError

    def validar(self, entidade: T) -> None:
        pass

    def criar(self, pessoa_id: UUID, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            self.repo.exigir_pessoa(pessoa_id, bloquear=True)
            self.repo.exigir_referencia(dados.id_referencia)
            entidade: T = self.construir(pessoa_id, dados, sujeito)
            self.preencher(entidade, dados)
            self.validar(entidade)
            self.sessao.add(entidade)
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado

    def editar(self, pessoa_id: UUID, identificador: UUID, dados: I, sujeito: str) -> V:
        with self.sessao.begin():
            self.repo.exigir_pessoa(pessoa_id, bloquear=True)
            self.repo.exigir_referencia(dados.id_referencia)
            entidade: T = self.repo.obter(pessoa_id, identificador)
            self.preencher(entidade, dados)
            self.validar(entidade)
            auditar(entidade, sujeito)
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado

    def inativar(self, pessoa_id: UUID, identificador: UUID, sujeito: str) -> V:
        with self.sessao.begin():
            self.repo.exigir_pessoa(pessoa_id, ativo=False, bloquear=True)
            entidade: T = self.repo.obter(pessoa_id, identificador)
            auditar(entidade, sujeito)
            entidade.inativado_em = entidade.atualizado_em
            self.sessao.flush()
            resultado: V = self.visualizar(entidade)
        return resultado


class PessoaInstituicaoService(
    VinculoService[PessoaInstituicao, PessoaInstituicaoInput, PessoaInstituicaoVM]
):
    def __init__(self, sessao: Session) -> None:
        super().__init__(
            sessao,
            PessoaInstituicao,
            pessoa_instituicao,
            instituicoes,
            "instituicao_id",
            PessoaInstituicaoVM,
        )

    def construir(
        self, pessoa_id: UUID, dados: PessoaInstituicaoInput, sujeito: str
    ) -> PessoaInstituicao:
        return PessoaInstituicao(
            pessoa_id=pessoa_id,
            instituicao_id=dados.instituicao_id,
            tipo_vinculo=dados.tipo_vinculo,
            inicio_em=dados.inicio_em,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: PessoaInstituicao, dados: PessoaInstituicaoInput) -> None:
        entidade.instituicao_id = dados.instituicao_id
        entidade.tipo_vinculo = dados.tipo_vinculo
        entidade.inicio_em = dados.inicio_em
        entidade.fim_em = dados.fim_em
        entidade.situacao_validacao = dados.situacao_validacao

    def validar(self, entidade: PessoaInstituicao) -> None:
        if self.repo.ha_sobreposicao(
            entidade.pessoa_id,
            entidade.instituicao_id,
            entidade.tipo_vinculo,
            entidade.inicio_em,
            entidade.fim_em,
            entidade.id,
        ):
            raise ErroNegocio(
                409,
                "Vínculo sobreposto",
                "Já existe vínculo deste tipo com a instituição no período informado.",
            )


class PessoaProfissaoService(
    VinculoService[PessoaProfissao, PessoaProfissaoInput, PessoaProfissaoVM]
):
    def __init__(self, sessao: Session) -> None:
        super().__init__(
            sessao, PessoaProfissao, pessoa_profissao, profissoes, "profissao_id", PessoaProfissaoVM
        )

    def construir(
        self, pessoa_id: UUID, dados: PessoaProfissaoInput, sujeito: str
    ) -> PessoaProfissao:
        return PessoaProfissao(
            pessoa_id=pessoa_id,
            profissao_id=dados.profissao_id,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: PessoaProfissao, dados: PessoaProfissaoInput) -> None:
        entidade.profissao_id = dados.profissao_id
        entidade.registro_profissional = dados.registro_profissional
        entidade.orgao_registro = dados.orgao_registro
        entidade.uf_registro = dados.uf_registro
        entidade.validade_em = dados.validade_em
        entidade.situacao_validacao = dados.situacao_validacao


class PessoaCursoService(VinculoService[PessoaCurso, PessoaCursoInput, PessoaCursoVM]):
    def __init__(self, sessao: Session) -> None:
        super().__init__(sessao, PessoaCurso, pessoa_curso, cursos, "curso_id", PessoaCursoVM)

    def construir(self, pessoa_id: UUID, dados: PessoaCursoInput, sujeito: str) -> PessoaCurso:
        return PessoaCurso(
            pessoa_id=pessoa_id,
            curso_id=dados.curso_id,
            instituicao_emissora=dados.instituicao_emissora,
            conclusao_em=dados.conclusao_em,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )

    def preencher(self, entidade: PessoaCurso, dados: PessoaCursoInput) -> None:
        entidade.curso_id = dados.curso_id
        entidade.instituicao_emissora = dados.instituicao_emissora
        entidade.conclusao_em = dados.conclusao_em
        entidade.validade_em = dados.validade_em
        entidade.carga_horaria = dados.carga_horaria
        entidade.comprovante_referencia = dados.comprovante_referencia
        entidade.situacao_validacao = dados.situacao_validacao

from uuid import UUID

from sqlalchemy.orm import Session

from business.view_models.cadastros import (
    CadastroPublicoPessoaInput,
    ContatoInput,
    InstituicaoInput,
    InstituicaoVM,
    PessoaInput,
    PessoaVM,
    VerificacaoEmailInput,
)
from core.entity.cadastros import Contato, Instituicao, Pessoa, SituacaoCadastral, agora_utc
from core.http.contratos import ErroNegocio
from infra.configurations.cadastros import instituicoes, pessoas
from infra.database.repositorio import Repositorio


def preencher_contato(destino: Contato, dados: ContatoInput, sujeito: str) -> None:
    destino.nome = dados.nome
    destino.municipio_codigo_ibge = dados.municipio_codigo_ibge
    destino.uf = dados.uf
    destino.email_contato = dados.email_contato
    destino.telefone_contato = dados.telefone_contato
    destino.latitude = dados.latitude
    destino.longitude = dados.longitude
    destino.situacao_cadastral = dados.situacao_cadastral
    destino.atualizado_por = sujeito
    destino.atualizado_em = agora_utc()


class InstituicaoService:
    def __init__(self, sessao: Session) -> None:
        self.sessao: Session = sessao
        self.repo: Repositorio[Instituicao] = Repositorio(sessao, Instituicao, instituicoes)

    def listar(
        self, limite: int, deslocamento: int, busca: str | None = None
    ) -> list[InstituicaoVM]:
        return [
            InstituicaoVM.model_validate(i) for i in self.repo.listar(limite, deslocamento, busca)
        ]

    def obter_entidade(self, identificador: UUID) -> Instituicao:
        entidade: Instituicao | None = self.repo.obter(identificador)
        if entidade is None:
            raise ErroNegocio(404, "Instituição não encontrada", "Cadastro inexistente ou inativo.")
        return entidade

    def obter(self, identificador: UUID) -> InstituicaoVM:
        return InstituicaoVM.model_validate(self.obter_entidade(identificador))

    def criar(self, dados: InstituicaoInput, sujeito: str) -> InstituicaoVM:
        entidade: Instituicao = Instituicao(
            nome=dados.nome,
            municipio_codigo_ibge=dados.municipio_codigo_ibge,
            uf=dados.uf,
            tipo=dados.tipo,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )
        self.preencher(entidade, dados, sujeito)
        with self.sessao.begin():
            self.repo.adicionar(entidade)
            self.sessao.flush()
            resultado: InstituicaoVM = InstituicaoVM.model_validate(entidade)
        return resultado

    def preencher(self, entidade: Instituicao, dados: InstituicaoInput, sujeito: str) -> None:
        preencher_contato(entidade, dados, sujeito)
        entidade.tipo = dados.tipo
        entidade.razao_social = dados.razao_social
        entidade.cnpj = dados.cnpj
        entidade.descricao = dados.descricao

    def editar(self, identificador: UUID, dados: InstituicaoInput, sujeito: str) -> InstituicaoVM:
        with self.sessao.begin():
            entidade: Instituicao = self.obter_entidade(identificador)
            self.preencher(entidade, dados, sujeito)
            self.sessao.flush()
            resultado: InstituicaoVM = InstituicaoVM.model_validate(entidade)
        return resultado

    def inativar(self, identificador: UUID, sujeito: str) -> InstituicaoVM:
        with self.sessao.begin():
            entidade: Instituicao = self.obter_entidade(identificador)
            entidade.inativado_em = agora_utc()
            entidade.atualizado_em = entidade.inativado_em
            entidade.atualizado_por = sujeito
            self.sessao.flush()
            resultado: InstituicaoVM = InstituicaoVM.model_validate(entidade)
        return resultado


class PessoaService:
    def __init__(self, sessao: Session) -> None:
        self.sessao: Session = sessao
        self.repo: Repositorio[Pessoa] = Repositorio(sessao, Pessoa, pessoas)

    def listar(self, limite: int, deslocamento: int, busca: str | None = None) -> list[PessoaVM]:
        return [PessoaVM.model_validate(p) for p in self.repo.listar(limite, deslocamento, busca)]

    def obter_entidade(self, identificador: UUID) -> Pessoa:
        entidade: Pessoa | None = self.repo.obter(identificador)
        if entidade is None:
            raise ErroNegocio(404, "Pessoa não encontrada", "Cadastro inexistente ou inativo.")
        return entidade

    def obter(self, identificador: UUID) -> PessoaVM:
        return PessoaVM.model_validate(self.obter_entidade(identificador))

    def criar(self, dados: PessoaInput, sujeito: str) -> PessoaVM:
        entidade: Pessoa = Pessoa(
            nome=dados.nome,
            municipio_codigo_ibge=dados.municipio_codigo_ibge,
            uf=dados.uf,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )
        preencher_contato(entidade, dados, sujeito)
        with self.sessao.begin():
            self.repo.adicionar(entidade)
            self.sessao.flush()
            resultado: PessoaVM = PessoaVM.model_validate(entidade)
        return resultado

    def autocadastrar(self, dados: CadastroPublicoPessoaInput) -> PessoaVM:
        sujeito: str = "autocadastro-publico"
        entidade: Pessoa = Pessoa(
            nome=dados.nome,
            municipio_codigo_ibge=dados.municipio_codigo_ibge,
            uf=dados.uf,
            criado_por=sujeito,
            atualizado_por=sujeito,
        )
        preencher_contato(entidade, dados, sujeito)
        entidade.situacao_cadastral = SituacaoCadastral.PENDENTE
        with self.sessao.begin():
            self.repo.adicionar(entidade)
            self.sessao.flush()
            resultado: PessoaVM = PessoaVM.model_validate(entidade)
        return resultado

    def verificar_por_email(self, dados: VerificacaoEmailInput) -> PessoaVM:
        with self.sessao.begin():
            entidade: Pessoa | None = self.repo.obter_por_email(dados.email_contato)
            if entidade is None:
                raise ErroNegocio(
                    404,
                    "Cadastro não encontrado",
                    "Nenhum cadastro ativo foi localizado para o e-mail informado.",
                )
            entidade.situacao_cadastral = SituacaoCadastral.VALIDADA
            entidade.atualizado_em = agora_utc()
            entidade.atualizado_por = "verificacao-email"
            self.sessao.flush()
            resultado: PessoaVM = PessoaVM.model_validate(entidade)
        return resultado

    def editar(self, identificador: UUID, dados: PessoaInput, sujeito: str) -> PessoaVM:
        with self.sessao.begin():
            entidade: Pessoa = self.obter_entidade(identificador)
            preencher_contato(entidade, dados, sujeito)
            self.sessao.flush()
            resultado: PessoaVM = PessoaVM.model_validate(entidade)
        return resultado

    def inativar(self, identificador: UUID, sujeito: str) -> PessoaVM:
        with self.sessao.begin():
            entidade: Pessoa = self.obter_entidade(identificador)
            entidade.inativado_em = agora_utc()
            entidade.atualizado_em = entidade.inativado_em
            entidade.atualizado_por = sujeito
            self.sessao.flush()
            resultado: PessoaVM = PessoaVM.model_validate(entidade)
        return resultado


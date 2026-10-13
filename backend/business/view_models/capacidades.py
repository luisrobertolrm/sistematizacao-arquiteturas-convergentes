from uuid import UUID

from pydantic import Field, field_validator

from business.view_models.cadastros import AuditoriaVM
from business.view_models.qualificacoes import Entrada


class CatalogoCodigoInput(Entrada):
    codigo: str = Field(min_length=1, max_length=50, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    nome: str = Field(min_length=2, max_length=200)

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo(cls, valor: str) -> str:
        return valor.strip().lower() if isinstance(valor, str) else valor


class UnidadeMedidaInput(CatalogoCodigoInput):
    simbolo: str = Field(min_length=1, max_length=30)


class CategoriaAtividadeInput(CatalogoCodigoInput):
    descricao: str | None = Field(default=None, max_length=4000)

    @field_validator("descricao")
    @classmethod
    def vazio_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class AtividadeInput(CatalogoCodigoInput):
    descricao: str = Field(min_length=2, max_length=4000)
    categoria_id: UUID
    id_unidade_capacidade: UUID | None = None
    orientacoes: str | None = Field(default=None, max_length=4000)
    restricoes: str | None = Field(default=None, max_length=4000)

    @field_validator("orientacoes", "restricoes")
    @classmethod
    def vazio_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class AtividadeTermoInput(Entrada):
    termo: str = Field(min_length=2, max_length=200)

    @field_validator("termo", mode="before")
    @classmethod
    def normalizar_termo(cls, valor: str) -> str:
        return " ".join(valor.split()).lower() if isinstance(valor, str) else valor


class UnidadeMedidaVM(UnidadeMedidaInput, AuditoriaVM):
    pass


class CategoriaAtividadeVM(CategoriaAtividadeInput, AuditoriaVM):
    pass


class AtividadeVM(AtividadeInput, AuditoriaVM):
    hash_conteudo_semantico: str
    categoria_nome: str = ""
    categoria_inativa: bool = False
    unidade_nome: str | None = None
    unidade_inativa: bool = False


class AtividadeTermoVM(AtividadeTermoInput, AuditoriaVM):
    atividade_id: UUID

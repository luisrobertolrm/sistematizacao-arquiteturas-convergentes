import re
from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from core.entity.cadastros import SituacaoCadastral, TipoInstituicao

UFS: frozenset[str] = frozenset(
    {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }
)


class ContatoInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, from_attributes=True)
    nome: str = Field(min_length=2, max_length=200)
    municipio_codigo_ibge: str = Field(pattern=r"^[0-9]{7}$")
    uf: str
    email_contato: str | None = Field(default=None, max_length=320)
    telefone_contato: str | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal | None = Field(
        default=None, ge=-180, le=180, max_digits=10, decimal_places=7
    )
    situacao_cadastral: SituacaoCadastral = SituacaoCadastral.PENDENTE

    @field_validator("uf")
    @classmethod
    def validar_uf(cls, valor: str) -> str:
        normalizada: str = valor.upper()
        if normalizada not in UFS:
            raise ValueError("UF inválida")
        return normalizada

    @field_validator("email_contato")
    @classmethod
    def validar_email(cls, valor: str | None) -> str | None:
        if not valor:
            return None
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ValueError("Email inválido")
        return valor

    @field_validator("telefone_contato")
    @classmethod
    def validar_telefone(cls, valor: str | None) -> str | None:
        if not valor:
            return None
        normalizado: str = re.sub(r"[\s().-]", "", valor)
        if not re.fullmatch(r"\+?[0-9]{8,15}", normalizado):
            raise ValueError("Telefone inválido")
        return normalizado

    @model_validator(mode="after")
    def validar_coordenadas(self) -> Self:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude e longitude devem ser informadas juntas")
        return self


class InstituicaoInput(ContatoInput):
    tipo: TipoInstituicao
    razao_social: str | None = Field(default=None, max_length=200)
    cnpj: str | None = None
    descricao: str | None = Field(default=None, max_length=4000)

    @field_validator("cnpj")
    @classmethod
    def normalizar_cnpj(cls, valor: str | None) -> str | None:
        if not valor:
            return None
        normalizado: str = re.sub(r"[./\s-]", "", valor).upper()
        # Formato numérico ou alfanumérico; verificação de DV não é prometida aqui.
        if not re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", normalizado):
            raise ValueError("CNPJ deve ter 14 posições, com dois dígitos finais numéricos")
        return normalizado


class PessoaInput(ContatoInput):
    pass


class AuditoriaVM(BaseModel):
    id: UUID
    criado_em: datetime
    atualizado_em: datetime
    inativado_em: datetime | None


class InstituicaoVM(InstituicaoInput, AuditoriaVM):
    pass


class PessoaVM(PessoaInput, AuditoriaVM):
    pass


class StatusVM(BaseModel):
    status: str

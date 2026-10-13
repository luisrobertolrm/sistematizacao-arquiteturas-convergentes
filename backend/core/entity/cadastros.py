from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4


def agora_utc() -> datetime:
    return datetime.now(UTC)


class SituacaoCadastral(StrEnum):
    PENDENTE = "pendente"
    VALIDADA = "validada"
    REJEITADA = "rejeitada"


class TipoInstituicao(StrEnum):
    ORGAO_PUBLICO = "orgao_publico"
    EMPRESA = "empresa"
    ONG = "ong"
    ASSOCIACAO = "associacao"


@dataclass(kw_only=True)
class Entidade:
    id: UUID = field(default_factory=uuid4)
    criado_em: datetime = field(default_factory=agora_utc)
    atualizado_em: datetime = field(default_factory=agora_utc)
    inativado_em: datetime | None = None
    criado_por: str
    atualizado_por: str


@dataclass(kw_only=True)
class Contato(Entidade):
    nome: str
    municipio_codigo_ibge: str
    uf: str
    situacao_cadastral: SituacaoCadastral = SituacaoCadastral.PENDENTE
    email_contato: str | None = None
    telefone_contato: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


@dataclass(kw_only=True)
class Instituicao(Contato):
    tipo: TipoInstituicao
    razao_social: str | None = None
    cnpj: str | None = None
    descricao: str | None = None


@dataclass(kw_only=True)
class Pessoa(Contato):
    pass

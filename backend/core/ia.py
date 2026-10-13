from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class CandidatoAtividade(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_atividade: UUID
    nome: str
    descricao: str


class ItemPropostaIA(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_atividade: UUID
    justificativa: str = Field(min_length=1, max_length=4000)


class PropostaIA(BaseModel):
    model_config = ConfigDict(extra="forbid")
    itens: list[ItemPropostaIA]
    pendencias: list[str]


class ContextoIA(BaseModel):
    necessidade: str
    candidatos: list[CandidatoAtividade]


class ConfiguracaoTextoIA(BaseModel):
    id_modelo: UUID
    identificador_modelo: str
    url_base: str
    token: SecretStr = Field(repr=False)

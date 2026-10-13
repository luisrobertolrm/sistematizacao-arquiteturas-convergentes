from decimal import Decimal
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class ContratoIA(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PessoaSugerida(ContratoIA):
    id_pessoa: UUID
    id_oferta_atividade: UUID
    papel_sugerido: str = Field(min_length=2, max_length=200)


class InstituicaoSugerida(ContratoIA):
    id_instituicao: UUID
    id_oferta_atividade: UUID


class RecursoSugerido(ContratoIA):
    id_recurso: UUID
    quantidade_sugerida: Decimal = Field(gt=0, max_digits=18, decimal_places=4)


class ItemSugerido(ContratoIA):
    id_demanda_item: UUID
    quantidade_sugerida: Decimal = Field(ge=0, max_digits=18, decimal_places=4)
    justificativa: str = Field(min_length=2, max_length=4000)
    pessoas: list[PessoaSugerida] = Field(max_length=30)
    instituicoes: list[InstituicaoSugerida] = Field(max_length=30)
    recursos: list[RecursoSugerido] = Field(max_length=30)


class PropostaDemanda(ContratoIA):
    justificativa: str = Field(min_length=2, max_length=4000)
    pendencias: list[str] = Field(max_length=100)
    itens: list[ItemSugerido] = Field(max_length=100)

    @field_validator("pendencias")
    @classmethod
    def limitar_pendencias(cls, v: list[str]) -> list[str]:
        if any(not p.strip() or len(p) > 4000 for p in v):
            raise ValueError("Pendências devem ter 1 a 4000 caracteres")
        return v


class ConfiguracaoModelo(ContratoIA):
    id_modelo: UUID
    identificador_modelo: str
    revisao: str | None
    dimensao: int | None
    url_base: str
    token: SecretStr = Field(repr=False)
    sem_autenticacao: bool = False


class ClienteEmbedding(Protocol):
    def gerar(self, textos: list[str]) -> list[list[float]]: ...


class ClienteInferencia(Protocol):
    def gerar(self, contexto: str) -> PropostaDemanda: ...


class FabricaClientesIA(Protocol):
    def embedding(self, config: ConfiguracaoModelo) -> ClienteEmbedding: ...
    def inferencia(self, config: ConfiguracaoModelo) -> ClienteInferencia: ...

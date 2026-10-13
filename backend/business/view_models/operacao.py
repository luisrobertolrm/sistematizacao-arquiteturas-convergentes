from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal, Self
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import AwareDatetime, Field, SecretStr, StrictBool, field_validator, model_validator

from business.view_models.cadastros import AuditoriaVM
from business.view_models.qualificacoes import Entrada
from core.entity.operacao import (
    FinalidadeModeloIA,
    PrioridadeDemanda,
    SituacaoDemanda,
    SituacaoIndexacao,
    SituacaoRecomendacao,
    TipoAutenticacaoIA,
)
from core.ia_operacao import (
    InstituicaoSugerida as InstituicaoSugerida,
)
from core.ia_operacao import (
    ItemSugerido as ItemSugerido,
)
from core.ia_operacao import (
    PessoaSugerida as PessoaSugerida,
)
from core.ia_operacao import (
    PropostaDemanda as PropostaDemanda,
)
from core.ia_operacao import (
    RecursoSugerido as RecursoSugerido,
)


class ConexaoInput(Entrada):
    nome: str = Field(min_length=2, max_length=200)
    provedor: Literal["openai_compativel"] = "openai_compativel"
    url_base: str = Field(max_length=2000)
    tipo_autenticacao: TipoAutenticacaoIA = TipoAutenticacaoIA.BEARER
    token: SecretStr | None = Field(default=None, repr=False)

    @field_validator("url_base")
    @classmethod
    def validar_url(cls, valor: str) -> str:
        u = urlsplit(valor)
        if (
            u.scheme not in {"http", "https"}
            or not u.hostname
            or any((u.username, u.password, u.query, u.fragment))
        ):
            raise ValueError("Informe URL HTTP(S) sem credenciais, query ou fragmento")
        if u.scheme == "http" and u.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("HTTP sem TLS somente em loopback")
        return valor.rstrip("/")

    @field_validator("token")
    @classmethod
    def validar_token(cls, valor: SecretStr | None) -> SecretStr | None:
        if valor is not None and not 1 <= len(valor.get_secret_value()) <= 8192:
            raise ValueError("Credencial deve ter 1 a 8192 caracteres")
        return valor


class ConexaoVM(AuditoriaVM, Entrada):
    nome: str
    provedor: str
    url_base: str
    tipo_autenticacao: TipoAutenticacaoIA
    tem_token: bool = False
    identificador_chave: str | None


class ModeloInput(Entrada):
    id_conexao: UUID
    identificador_modelo: str = Field(min_length=1, max_length=200)
    revisao: str | None = Field(default=None, min_length=1, max_length=200)
    finalidade: FinalidadeModeloIA
    dimensao: int | None = Field(default=None, ge=1, le=16384)
    ativo: StrictBool = False

    @model_validator(mode="after")
    def validar_dimensao(self) -> Self:
        if (self.finalidade == FinalidadeModeloIA.EMBEDDING) != (self.dimensao is not None):
            raise ValueError("Dimensão é obrigatória somente para embedding")
        return self


class ModeloVM(ModeloInput, AuditoriaVM):
    conexao_nome: str = ""
    conexao_inativa: bool = False


class DemandaItemInput(Entrada):
    id: UUID | None = None
    id_atividade: UUID | None = None
    id_tipo_recurso: UUID | None = None
    id_unidade_medida: UUID
    quantidade_solicitada: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    observacoes: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def necessidade_exclusiva(self) -> Self:
        if (self.id_atividade is None) == (self.id_tipo_recurso is None):
            raise ValueError("Informe exatamente uma atividade ou tipo de recurso")
        return self


class DemandaInput(Entrada):
    id_area_afetada: UUID
    id_pessoa_solicitante: UUID
    titulo: str = Field(min_length=2, max_length=200)
    descricao: str = Field(min_length=2, max_length=4000)
    prioridade: PrioridadeDemanda = PrioridadeDemanda.NORMAL
    inicio_previsto_em: AwareDatetime
    prazo_em: AwareDatetime
    situacao: SituacaoDemanda = SituacaoDemanda.ABERTA
    itens: list[DemandaItemInput] = Field(min_length=1, max_length=100)

    @field_validator("inicio_previsto_em", "prazo_em")
    @classmethod
    def utc(cls, v: datetime) -> datetime:
        return v.astimezone(UTC)

    @model_validator(mode="after")
    def validar_pedido(self) -> Self:
        if self.prazo_em < self.inicio_previsto_em:
            raise ValueError("Prazo não pode anteceder início previsto")
        ids = [i.id for i in self.itens if i.id is not None]
        if len(ids) != len(set(ids)):
            raise ValueError("Itens repetidos")
        return self


class DemandaItemVM(AuditoriaVM, Entrada):
    id_demanda: UUID
    id_atividade: UUID | None
    id_tipo_recurso: UUID | None
    id_unidade_medida: UUID
    quantidade_solicitada: Decimal
    observacoes: str | None
    necessidade_nome: str = ""
    unidade_simbolo: str = ""


class DemandaVM(AuditoriaVM, Entrada):
    id_area_afetada: UUID
    id_pessoa_solicitante: UUID
    titulo: str
    descricao: str
    prioridade: PrioridadeDemanda
    inicio_previsto_em: datetime
    prazo_em: datetime
    situacao: SituacaoDemanda
    area_nome: str = ""
    solicitante_nome: str = ""
    itens: list[DemandaItemVM] = Field(default_factory=list)


class IndiceVM(AuditoriaVM, Entrada):
    id_atividade: UUID
    id_modelo: UUID
    hash_atividade_origem: str
    situacao_indexacao: SituacaoIndexacao
    indexado_em: datetime | None
    atualizado: bool = False
    atividade_nome: str = ""


class IndexarInput(Entrada):
    id_modelo: UUID
    ids_atividades: list[UUID] = Field(min_length=1, max_length=50)


class BuscaInput(Entrada):
    texto: str = Field(min_length=2, max_length=4000)
    limite: int = Field(default=10, ge=1, le=30)


class ResultadoBusca(Entrada):
    id_atividade: UUID
    nome: str
    similaridade: float


class BuscaVM(Entrada):
    id_modelo: UUID
    resultados: list[ResultadoBusca]


class DecisaoInput(Entrada):
    situacao: Literal["aprovada", "rejeitada"]
    justificativa: str = Field(min_length=2, max_length=4000)


class RecomendacaoItemVM(ItemSugerido):
    id: UUID


class RecomendacaoVM(AuditoriaVM, Entrada):
    nomes_candidatos: dict[UUID, str] = Field(default_factory=dict)
    id_demanda: UUID
    id_modelo_embedding: UUID
    id_modelo_inferencia: UUID
    hash_contexto: str
    gerada_em: datetime
    justificativa: str
    pendencias: list[str]
    situacao: SituacaoRecomendacao
    decidida_em: datetime | None
    decidida_por: str | None
    justificativa_decisao: str | None
    itens: list[RecomendacaoItemVM] = Field(default_factory=list)

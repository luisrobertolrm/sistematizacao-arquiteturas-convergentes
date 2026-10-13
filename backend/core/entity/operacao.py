from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from core.entity.cadastros import Entidade, agora_utc


class FinalidadeModeloIA(StrEnum):
    EMBEDDING = "embedding"
    TEXTO = "inferencia_texto"


class TipoAutenticacaoIA(StrEnum):
    BEARER = "bearer"
    NENHUMA = "nenhuma"


@dataclass(kw_only=True)
class ConexaoIA(Entidade):
    nome: str
    provedor: str
    url_base: str
    tipo_autenticacao: TipoAutenticacaoIA
    token_criptografado: bytes | None = field(default=None, repr=False)
    identificador_chave: str | None = None


@dataclass(kw_only=True)
class ModeloIA(Entidade):
    id_conexao: UUID
    identificador_modelo: str
    finalidade: FinalidadeModeloIA
    revisao: str | None = None
    dimensao: int | None = None
    ativo: bool = False


class PrioridadeDemanda(StrEnum):
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class SituacaoDemanda(StrEnum):
    ABERTA = "aberta"
    EM_ATENDIMENTO = "em_atendimento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


@dataclass(kw_only=True)
class Demanda(Entidade):
    id_area_afetada: UUID
    id_pessoa_solicitante: UUID
    titulo: str
    descricao: str
    prioridade: PrioridadeDemanda
    inicio_previsto_em: datetime
    prazo_em: datetime
    situacao: SituacaoDemanda = SituacaoDemanda.ABERTA


@dataclass(kw_only=True)
class DemandaItem(Entidade):
    id_demanda: UUID
    id_unidade_medida: UUID
    quantidade_solicitada: Decimal
    id_atividade: UUID | None = None
    id_tipo_recurso: UUID | None = None
    observacoes: str | None = None


class SituacaoIndexacao(StrEnum):
    PENDENTE = "pendente"
    PRONTA = "pronta"


@dataclass(kw_only=True)
class AtividadeIndiceSemantico(Entidade):
    id_atividade: UUID
    id_modelo: UUID
    hash_atividade_origem: str
    embedding: list[float] | None = None
    situacao_indexacao: SituacaoIndexacao = SituacaoIndexacao.PENDENTE
    indexado_em: datetime | None = None


class SituacaoRecomendacao(StrEnum):
    GERADA = "gerada"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"


@dataclass(kw_only=True)
class Recomendacao(Entidade):
    id_demanda: UUID
    id_modelo_embedding: UUID
    id_modelo_inferencia: UUID
    hash_contexto: str
    justificativa: str
    pendencias: list[str]
    gerada_em: datetime = field(default_factory=agora_utc)
    situacao: SituacaoRecomendacao = SituacaoRecomendacao.GERADA
    decidida_em: datetime | None = None
    decidida_por: str | None = None
    justificativa_decisao: str | None = None


@dataclass(kw_only=True)
class RecomendacaoItem(Entidade):
    id_recomendacao: UUID
    id_demanda_item: UUID
    quantidade_sugerida: Decimal
    justificativa: str


@dataclass(kw_only=True)
class RecomendacaoPessoa(Entidade):
    id_recomendacao_item: UUID
    id_pessoa: UUID
    id_oferta_atividade: UUID
    papel_sugerido: str


@dataclass(kw_only=True)
class RecomendacaoInstituicao(Entidade):
    id_recomendacao_item: UUID
    id_instituicao: UUID
    id_oferta_atividade: UUID


@dataclass(kw_only=True)
class RecomendacaoRecurso(Entidade):
    id_recomendacao_item: UUID
    id_recurso: UUID
    quantidade_sugerida: Decimal

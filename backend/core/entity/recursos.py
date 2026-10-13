from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from core.entity.cadastros import Entidade
from core.entity.qualificacoes import SituacaoValidacao


class CategoriaRecurso(StrEnum):
    VEICULO = "veiculo"
    EQUIPAMENTO = "equipamento"
    MATERIAL = "material"
    INSUMO = "insumo"


class ModoControleRecurso(StrEnum):
    INDIVIDUAL = "individual"
    ESTOQUE = "estoque"


class EstadoRecurso(StrEnum):
    OPERACIONAL = "operacional"
    EM_MANUTENCAO = "em_manutencao"
    INDISPONIVEL = "indisponivel"


@dataclass(kw_only=True)
class TipoRecurso(Entidade):
    nome: str
    categoria: CategoriaRecurso
    id_unidade_medida: UUID
    modo_controle: ModoControleRecurso
    hash_conteudo_semantico: str
    descricao: str | None = None


@dataclass(kw_only=True)
class Responsavel(Entidade):
    instituicao_id: UUID | None = None
    pessoa_id: UUID | None = None


@dataclass(kw_only=True)
class Recurso(Responsavel):
    tipo_recurso_id: UUID
    nome: str
    quantidade_total: Decimal
    municipio_codigo_ibge: str
    estado_operacional: EstadoRecurso = EstadoRecurso.OPERACIONAL
    descricao: str | None = None
    identificacao: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


@dataclass(kw_only=True)
class OfertaAtividade(Responsavel):
    atividade_id: UUID
    municipio_atendimento_codigo_ibge: str
    descricao_complementar: str | None = None
    capacidade_declarada: Decimal | None = None
    situacao_validacao: SituacaoValidacao = SituacaoValidacao.PENDENTE
    validado_em: datetime | None = None


@dataclass(kw_only=True)
class OfertaAtividadeRecurso(Entidade):
    oferta_atividade_id: UUID
    recurso_id: UUID
    quantidade_prevista: Decimal

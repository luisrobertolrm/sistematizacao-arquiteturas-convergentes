from enum import StrEnum

from alembic import op
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    MetaData,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.sql.schema import SchemaItem

"""Snapshot independente de entidades e mapeamentos atuais."""


revision: str = "0009_recomendacoes"
down_revision: str | None = "0008_indices"
branch_labels: str | None = None
depends_on: str | None = None

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class FinalidadeModeloIA(StrEnum):
    EMBEDDING = "embedding"
    TEXTO = "inferencia_texto"


class TipoAutenticacaoIA(StrEnum):
    BEARER = "bearer"
    NENHUMA = "nenhuma"


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


class SituacaoIndexacao(StrEnum):
    PENDENTE = "pendente"
    PRONTA = "pronta"


class SituacaoRecomendacao(StrEnum):
    GERADA = "gerada"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"


def auditoria() -> list[SchemaItem]:
    return [
        Column("id", Uuid, primary_key=True),
        Column("criado_em", DateTime(timezone=True), nullable=False),
        Column("atualizado_em", DateTime(timezone=True), nullable=False),
        Column("inativado_em", DateTime(timezone=True)),
        Column("criado_por", String(200), nullable=False),
        Column("atualizado_por", String(200), nullable=False),
    ]


def enum_tipo[T: StrEnum](tipo: type[T], nome: str) -> Enum:
    return Enum(
        tipo,
        native_enum=False,
        create_constraint=True,
        name=nome,
        values_callable=lambda e: [str(v.value) for v in e],
    )


Table("demanda_itens", metadata, Column("id", Uuid, primary_key=True))
Table("demandas", metadata, Column("id", Uuid, primary_key=True))
Table("instituicoes", metadata, Column("id", Uuid, primary_key=True))
Table("modelo_ia", metadata, Column("id", Uuid, primary_key=True))
Table("ofertas_atividade", metadata, Column("id", Uuid, primary_key=True))
Table("pessoas", metadata, Column("id", Uuid, primary_key=True))
Table("recursos", metadata, Column("id", Uuid, primary_key=True))


recomendacoes = Table(
    "recomendacoes",
    metadata,
    *auditoria(),
    Column("id_demanda", Uuid, ForeignKey("demandas.id"), nullable=False),
    Column("id_modelo_embedding", Uuid, ForeignKey("modelo_ia.id"), nullable=False),
    Column("id_modelo_inferencia", Uuid, ForeignKey("modelo_ia.id"), nullable=False),
    Column("hash_contexto", String(64), nullable=False),
    Column("gerada_em", DateTime(timezone=True), nullable=False),
    Column("justificativa", String(4000), nullable=False),
    Column("pendencias", JSONB, nullable=False),
    Column("situacao", enum_tipo(SituacaoRecomendacao, "situacao_recomendacao"), nullable=False),
    Column("decidida_em", DateTime(timezone=True)),
    Column("decidida_por", String(200)),
    Column("justificativa_decisao", String(4000)),
    CheckConstraint(
        "(situacao = 'gerada' AND decidida_em IS NULL AND decidida_por IS NULL "
        "AND justificativa_decisao IS NULL) OR (situacao IN ('aprovada', 'rejeitada') "
        "AND decidida_em IS NOT NULL AND decidida_por IS NOT NULL "
        "AND justificativa_decisao IS NOT NULL)",
        name="decisao_coerente",
    ),
)

recomendacao_itens = Table(
    "recomendacao_itens",
    metadata,
    *auditoria(),
    Column("id_recomendacao", Uuid, ForeignKey("recomendacoes.id"), nullable=False),
    Column("id_demanda_item", Uuid, ForeignKey("demanda_itens.id"), nullable=False),
    Column("quantidade_sugerida", Numeric(18, 4), nullable=False),
    Column("justificativa", String(4000), nullable=False),
    CheckConstraint("quantidade_sugerida >= 0", name="quantidade_nao_negativa"),
    UniqueConstraint("id_recomendacao", "id_demanda_item"),
)

recomendacao_pessoas = Table(
    "recomendacao_pessoas",
    metadata,
    *auditoria(),
    Column("id_recomendacao_item", Uuid, ForeignKey("recomendacao_itens.id"), nullable=False),
    Column("id_pessoa", Uuid, ForeignKey("pessoas.id"), nullable=False),
    Column("id_oferta_atividade", Uuid, ForeignKey("ofertas_atividade.id"), nullable=False),
    Column("papel_sugerido", String(200), nullable=False),
    UniqueConstraint("id_recomendacao_item", "id_pessoa"),
)

recomendacao_instituicoes = Table(
    "recomendacao_instituicoes",
    metadata,
    *auditoria(),
    Column("id_recomendacao_item", Uuid, ForeignKey("recomendacao_itens.id"), nullable=False),
    Column("id_instituicao", Uuid, ForeignKey("instituicoes.id"), nullable=False),
    Column("id_oferta_atividade", Uuid, ForeignKey("ofertas_atividade.id"), nullable=False),
    UniqueConstraint("id_recomendacao_item", "id_oferta_atividade"),
)

recomendacao_recursos = Table(
    "recomendacao_recursos",
    metadata,
    *auditoria(),
    Column("id_recomendacao_item", Uuid, ForeignKey("recomendacao_itens.id"), nullable=False),
    Column("id_recurso", Uuid, ForeignKey("recursos.id"), nullable=False),
    Column("quantidade_sugerida", Numeric(18, 4), nullable=False),
    CheckConstraint("quantidade_sugerida > 0", name="quantidade_positiva"),
    UniqueConstraint("id_recomendacao_item", "id_recurso"),
)

for tabela in (
    recomendacoes,
    recomendacao_itens,
    recomendacao_pessoas,
    recomendacao_instituicoes,
    recomendacao_recursos,
):
    for coluna in tabela.c:
        if coluna.foreign_keys:
            Index(f"ix_{tabela.name}_{coluna.name}", coluna)


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(CreateTable(recomendacoes))
    for indice in sorted(recomendacoes.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))
    bind.execute(CreateTable(recomendacao_itens))
    for indice in sorted(recomendacao_itens.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))
    bind.execute(CreateTable(recomendacao_pessoas))
    for indice in sorted(recomendacao_pessoas.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))
    bind.execute(CreateTable(recomendacao_instituicoes))
    for indice in sorted(recomendacao_instituicoes.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))
    bind.execute(CreateTable(recomendacao_recursos))
    for indice in sorted(recomendacao_recursos.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))


def downgrade() -> None:
    op.drop_table("recomendacao_recursos")
    op.drop_table("recomendacao_instituicoes")
    op.drop_table("recomendacao_pessoas")
    op.drop_table("recomendacao_itens")
    op.drop_table("recomendacoes")

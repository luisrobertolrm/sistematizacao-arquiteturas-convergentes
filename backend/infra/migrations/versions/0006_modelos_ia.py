from enum import StrEnum

from alembic import op
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Table,
    Uuid,
    text,
)
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.sql.schema import SchemaItem

"""Snapshot independente de entidades e mapeamentos atuais."""


revision: str = "0006_modelos_ia"
down_revision: str | None = "0005_desastres_areas"
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


conexao_ia = Table(
    "conexao_ia",
    metadata,
    *auditoria(),
    Column("nome", String(200), nullable=False),
    Column("provedor", String(50), nullable=False),
    Column("url_base", String(2000), nullable=False),
    Column("tipo_autenticacao", enum_tipo(TipoAutenticacaoIA, "autenticacao_ia"), nullable=False),
    Column("token_criptografado", LargeBinary),
    Column("identificador_chave", String(100)),
    CheckConstraint("provedor = 'openai_compativel'", name="provedor_suportado"),
    CheckConstraint(
        "(tipo_autenticacao = 'bearer' AND token_criptografado IS NOT NULL "
        "AND identificador_chave IS NOT NULL) OR (tipo_autenticacao = 'nenhuma' "
        "AND token_criptografado IS NULL AND identificador_chave IS NULL)",
        name="credencial_coerente",
    ),
)

modelo_ia = Table(
    "modelo_ia",
    metadata,
    *auditoria(),
    Column("id_conexao", Uuid, ForeignKey("conexao_ia.id"), nullable=False),
    Column("identificador_modelo", String(200), nullable=False),
    Column("revisao", String(200)),
    Column("finalidade", enum_tipo(FinalidadeModeloIA, "finalidade_modelo"), nullable=False),
    Column("dimensao", Integer),
    Column("ativo", Boolean, nullable=False),
    CheckConstraint(
        "(finalidade = 'embedding' AND dimensao IS NOT NULL AND dimensao BETWEEN 1 AND 16384) OR "
        "(finalidade = 'inferencia_texto' AND dimensao IS NULL)",
        name="dimensao_coerente",
    ),
    CheckConstraint("NOT ativo OR inativado_em IS NULL", name="ativo_vigente"),
)

Index(
    "uq_modelo_ia_finalidade_ativa",
    modelo_ia.c.finalidade,
    unique=True,
    postgresql_where=text("ativo AND inativado_em IS NULL"),
)

Index("ix_modelo_ia_id_conexao", modelo_ia.c.id_conexao)


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(CreateTable(conexao_ia))
    for indice in sorted(conexao_ia.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))
    bind.execute(CreateTable(modelo_ia))
    for indice in sorted(modelo_ia.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))


def downgrade() -> None:
    op.drop_table("modelo_ia")
    op.drop_table("conexao_ia")

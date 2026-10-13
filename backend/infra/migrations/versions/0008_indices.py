from enum import StrEnum

from alembic import op
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Double,
    Enum,
    ForeignKey,
    Index,
    MetaData,
    String,
    Table,
    Uuid,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.sql.schema import SchemaItem

"""Snapshot independente de entidades e mapeamentos atuais."""


revision: str = "0008_indices"
down_revision: str | None = "0007_demandas"
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


Table("atividades", metadata, Column("id", Uuid, primary_key=True))
Table("modelo_ia", metadata, Column("id", Uuid, primary_key=True))


atividade_indice_semantico = Table(
    "atividade_indice_semantico",
    metadata,
    *auditoria(),
    Column("id_atividade", Uuid, ForeignKey("atividades.id"), nullable=False),
    Column("id_modelo", Uuid, ForeignKey("modelo_ia.id"), nullable=False),
    Column("hash_atividade_origem", String(64), nullable=False),
    Column("embedding", ARRAY(Double)),
    Column(
        "situacao_indexacao", enum_tipo(SituacaoIndexacao, "situacao_indexacao"), nullable=False
    ),
    Column("indexado_em", DateTime(timezone=True)),
    CheckConstraint(
        "(situacao_indexacao = 'pronta' AND embedding IS NOT NULL AND indexado_em IS NOT NULL) "
        "OR (situacao_indexacao = 'pendente' AND embedding IS NULL)",
        name="estado_vetor_coerente",
    ),
)

Index(
    "uq_atividade_indice_par",
    atividade_indice_semantico.c.id_atividade,
    atividade_indice_semantico.c.id_modelo,
    unique=True,
)

Index("ix_atividade_indice_semantico_id_modelo", atividade_indice_semantico.c.id_modelo)

SQL_VETOR: str = """
CREATE FUNCTION redesolidaria_validar_vetor() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE dimensao_modelo integer; finalidade_modelo text; hash_atual text;
BEGIN
    SELECT dimensao, finalidade INTO dimensao_modelo, finalidade_modelo
      FROM modelo_ia WHERE id = NEW.id_modelo FOR SHARE;
    IF finalidade_modelo IS DISTINCT FROM 'embedding' THEN
      RAISE EXCEPTION 'Finalidade de modelo inválida' USING ERRCODE = '23514';
    END IF;
    IF NEW.situacao_indexacao = 'pronta' THEN
      SELECT hash_conteudo_semantico INTO hash_atual FROM atividades
        WHERE id = NEW.id_atividade AND inativado_em IS NULL;
      IF NEW.hash_atividade_origem IS DISTINCT FROM hash_atual
        OR array_ndims(NEW.embedding) IS DISTINCT FROM 1
        OR cardinality(NEW.embedding) IS DISTINCT FROM dimensao_modelo
        OR EXISTS (SELECT 1 FROM unnest(NEW.embedding) x WHERE x IS NULL
          OR x IN ('NaN'::float8, 'Infinity'::float8, '-Infinity'::float8))
        OR NOT EXISTS (SELECT 1 FROM unnest(NEW.embedding) x WHERE x <> 0) THEN
        RAISE EXCEPTION 'Vetor ou hash incompatível' USING ERRCODE = '23514';
      END IF;
    END IF;
    RETURN NEW;
END $$
"""
SQL_INVALIDACAO: str = """
CREATE FUNCTION redesolidaria_invalidar_indices() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.hash_conteudo_semantico IS DISTINCT FROM OLD.hash_conteudo_semantico
    OR NEW.inativado_em IS DISTINCT FROM OLD.inativado_em THEN
    UPDATE atividade_indice_semantico SET embedding = NULL, situacao_indexacao = 'pendente',
      atualizado_em = NEW.atualizado_em, atualizado_por = NEW.atualizado_por
      WHERE id_atividade = NEW.id;
  END IF;
  RETURN NEW;
END $$
"""


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(CreateTable(atividade_indice_semantico))
    for indice in sorted(atividade_indice_semantico.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))

    op.execute(SQL_VETOR)
    op.execute(
        "CREATE TRIGGER validar_vetor BEFORE INSERT OR UPDATE ON atividade_indice_semantico "
        "FOR EACH ROW EXECUTE FUNCTION redesolidaria_validar_vetor()"
    )
    op.execute(SQL_INVALIDACAO)
    op.execute(
        "CREATE TRIGGER invalidar_indices AFTER UPDATE ON atividades "
        "FOR EACH ROW EXECUTE FUNCTION redesolidaria_invalidar_indices()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER invalidar_indices ON atividades")
    op.execute("DROP FUNCTION redesolidaria_invalidar_indices()")
    op.execute("DROP TRIGGER validar_vetor ON atividade_indice_semantico")
    op.execute("DROP FUNCTION redesolidaria_validar_vetor()")
    op.drop_table("atividade_indice_semantico")

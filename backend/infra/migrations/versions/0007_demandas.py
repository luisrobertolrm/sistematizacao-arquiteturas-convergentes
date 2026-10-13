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
    Uuid,
)
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.sql.schema import SchemaItem

"""Snapshot independente de entidades e mapeamentos atuais."""


revision: str = "0007_demandas"
down_revision: str | None = "0006_modelos_ia"
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


Table("areas_afetadas", metadata, Column("id", Uuid, primary_key=True))
Table("atividades", metadata, Column("id", Uuid, primary_key=True))
Table("pessoas", metadata, Column("id", Uuid, primary_key=True))
Table("tipos_recurso", metadata, Column("id", Uuid, primary_key=True))
Table("unidades_medida", metadata, Column("id", Uuid, primary_key=True))


demandas = Table(
    "demandas",
    metadata,
    *auditoria(),
    Column("id_area_afetada", Uuid, ForeignKey("areas_afetadas.id"), nullable=False),
    Column("id_pessoa_solicitante", Uuid, ForeignKey("pessoas.id"), nullable=False),
    Column("titulo", String(200), nullable=False),
    Column("descricao", String(4000), nullable=False),
    Column("prioridade", enum_tipo(PrioridadeDemanda, "prioridade_demanda"), nullable=False),
    Column("situacao", enum_tipo(SituacaoDemanda, "situacao_demanda"), nullable=False),
    Column("inicio_previsto_em", DateTime(timezone=True), nullable=False),
    Column("prazo_em", DateTime(timezone=True), nullable=False),
    CheckConstraint("prazo_em >= inicio_previsto_em", name="janela_valida"),
)

demanda_itens = Table(
    "demanda_itens",
    metadata,
    *auditoria(),
    Column("id_demanda", Uuid, ForeignKey("demandas.id"), nullable=False),
    Column("id_atividade", Uuid, ForeignKey("atividades.id")),
    Column("id_tipo_recurso", Uuid, ForeignKey("tipos_recurso.id")),
    Column("id_unidade_medida", Uuid, ForeignKey("unidades_medida.id"), nullable=False),
    Column("quantidade_solicitada", Numeric(18, 4), nullable=False),
    Column("observacoes", String(4000)),
    CheckConstraint(
        "(id_atividade IS NULL) <> (id_tipo_recurso IS NULL)", name="necessidade_exclusiva"
    ),
    CheckConstraint("quantidade_solicitada > 0", name="quantidade_positiva"),
)

for tabela, colunas in (
    (demandas, ["id_area_afetada", "id_pessoa_solicitante"]),
    (demanda_itens, ["id_demanda", "id_atividade", "id_tipo_recurso", "id_unidade_medida"]),
):
    for coluna in colunas:
        Index(f"ix_{tabela.name}_{coluna}", tabela.c[coluna])

SQL_UNIDADES: str = """
CREATE FUNCTION redesolidaria_proteger_unidade_pedido() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF TG_TABLE_NAME = 'atividades' THEN
    IF NEW.id_unidade_capacidade IS DISTINCT FROM OLD.id_unidade_capacidade
      AND EXISTS (SELECT 1 FROM demanda_itens WHERE id_atividade = OLD.id) THEN
      RAISE EXCEPTION 'Unidade utilizada em pedido' USING ERRCODE = '23514';
    END IF;
  ELSE
    IF NEW.id_unidade_medida IS DISTINCT FROM OLD.id_unidade_medida
      AND EXISTS (SELECT 1 FROM demanda_itens WHERE id_tipo_recurso = OLD.id) THEN
      RAISE EXCEPTION 'Unidade utilizada em pedido' USING ERRCODE = '23514';
    END IF;
  END IF;
  RETURN NEW;
END $$
"""


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(CreateTable(demandas))
    for indice in sorted(demandas.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))
    bind.execute(CreateTable(demanda_itens))
    for indice in sorted(demanda_itens.indexes, key=lambda i: i.name or ""):
        bind.execute(CreateIndex(indice))

    op.execute(SQL_UNIDADES)
    for tabela in ("atividades", "tipos_recurso"):
        op.execute(
            f"CREATE TRIGGER proteger_unidade_pedido BEFORE UPDATE ON {tabela} "
            "FOR EACH ROW EXECUTE FUNCTION redesolidaria_proteger_unidade_pedido()"
        )


def downgrade() -> None:
    for tabela in ("atividades", "tipos_recurso"):
        op.execute(f"DROP TRIGGER proteger_unidade_pedido ON {tabela}")
    op.execute("DROP FUNCTION redesolidaria_proteger_unidade_pedido()")
    op.drop_table("demanda_itens")
    op.drop_table("demandas")

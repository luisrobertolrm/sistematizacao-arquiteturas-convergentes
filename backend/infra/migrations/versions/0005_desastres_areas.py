"""Tipos de desastre, ocorrências, classificações e áreas; snapshot independente do domínio.

Revision ID: 0005_desastres_areas
Revises: 0004_recursos_ofertas
"""

from alembic import op
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    MetaData,
    String,
    Table,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.sql.schema import SchemaItem

revision: str = "0005_desastres_areas"
down_revision: str | None = "0004_recursos_ofertas"
branch_labels: str | None = None
depends_on: str | None = None

metadata: MetaData = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
# Apenas resolução dos FKs: as tabelas anteriores já existem e não são recriadas.
for nome in ("instituicoes",):
    Table(nome, metadata, Column("id", Uuid, primary_key=True))


def auditoria() -> list[SchemaItem]:
    return [
        Column("id", Uuid, primary_key=True),
        Column("criado_em", DateTime(timezone=True), nullable=False),
        Column("atualizado_em", DateTime(timezone=True), nullable=False),
        Column("inativado_em", DateTime(timezone=True)),
        Column("criado_por", String(200), nullable=False),
        Column("atualizado_por", String(200), nullable=False),
    ]


def catalogo_codigo(nome: str, *adicionais: SchemaItem) -> Table:
    tabela: Table = Table(
        nome,
        metadata,
        *auditoria(),
        Column("codigo", String(50), nullable=False, unique=True),
        Column("nome", String(200), nullable=False),
        CheckConstraint("codigo ~ '^[a-z0-9][a-z0-9_-]{0,49}$'", name="codigo_formato"),
        CheckConstraint("length(trim(nome)) >= 2", name="nome_obrigatorio"),
        *adicionais,
    )
    Index(f"ix_{nome}_nome_id", tabela.c.nome, tabela.c.id)
    return tabela


tipos_desastre: Table = catalogo_codigo(
    "tipos_desastre",
    Column("descricao", String(4000), nullable=False),
    CheckConstraint("length(trim(descricao)) >= 2", name="descricao_obrigatoria"),
)
desastres: Table = Table(
    "desastres",
    metadata,
    *auditoria(),
    Column("titulo", String(200), nullable=False),
    Column("descricao", String(4000), nullable=False),
    Column("inicio_em", DateTime(timezone=True), nullable=False),
    Column("encerramento_em", DateTime(timezone=True)),
    Column(
        "situacao",
        Enum(
            "em_monitoramento",
            "em_resposta",
            "em_recuperacao",
            "encerrado",
            name="situacao_desastre",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column(
        "id_instituicao_coordenadora",
        Uuid,
        ForeignKey("instituicoes.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    CheckConstraint("length(trim(titulo)) >= 2", name="titulo_obrigatorio"),
    CheckConstraint("length(trim(descricao)) >= 2", name="descricao_obrigatoria"),
    CheckConstraint("encerramento_em >= inicio_em", name="datas_coerentes"),
    CheckConstraint(
        "(situacao = 'encerrado') = (encerramento_em IS NOT NULL)", name="encerramento_situacao"
    ),
)
desastre_tipo: Table = Table(
    "desastre_tipo",
    metadata,
    *auditoria(),
    Column("id_desastre", Uuid, ForeignKey("desastres.id", ondelete="RESTRICT"), nullable=False),
    Column(
        "id_tipo_desastre",
        Uuid,
        ForeignKey("tipos_desastre.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("principal", Boolean, nullable=False),
)
Index(
    "uq_desastre_tipo_ativo",
    desastre_tipo.c.id_desastre,
    desastre_tipo.c.id_tipo_desastre,
    unique=True,
    postgresql_where=text("inativado_em IS NULL"),
)
Index(
    "uq_desastre_tipo_principal",
    desastre_tipo.c.id_desastre,
    unique=True,
    postgresql_where=text("inativado_em IS NULL AND principal"),
)
areas_afetadas: Table = Table(
    "areas_afetadas",
    metadata,
    *auditoria(),
    Column("id_desastre", Uuid, ForeignKey("desastres.id", ondelete="RESTRICT"), nullable=False),
    Column("nome", String(200), nullable=False),
    Column("descricao", String(4000), nullable=False),
    Column("municipio_codigo_ibge", String(7), nullable=False),
    Column("geometria", JSONB(), nullable=False),
    Column(
        "gravidade",
        Enum(
            "baixa",
            "moderada",
            "alta",
            "critica",
            name="gravidade_area",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column(
        "situacao",
        Enum(
            "em_avaliacao",
            "em_resposta",
            "em_recuperacao",
            "encerrada",
            name="situacao_area",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column("ultima_avaliacao_em", DateTime(timezone=True), nullable=False),
    CheckConstraint("length(trim(nome)) >= 2", name="nome_obrigatorio"),
    CheckConstraint("length(trim(descricao)) >= 2", name="descricao_obrigatoria"),
    CheckConstraint("municipio_codigo_ibge ~ '^[0-9]{7}$'", name="municipio_formato"),
    CheckConstraint(
        "COALESCE(CASE WHEN jsonb_typeof(geometria) = 'object' "
        "AND jsonb_typeof(geometria->'coordinates') = 'array' "
        "THEN geometria->>'type' = 'Polygon' "
        "AND jsonb_array_length(geometria->'coordinates') = 1 ELSE FALSE END, FALSE)",
        name="geometria_formato",
    ),
)
Index("ix_desastres_titulo_id", desastres.c.titulo, desastres.c.id)
Index(
    "ix_areas_afetadas_desastre_nome_id",
    areas_afetadas.c.id_desastre,
    areas_afetadas.c.nome,
    areas_afetadas.c.id,
)
for tabela, coluna in (
    (desastres, "id_instituicao_coordenadora"),
    (desastre_tipo, "id_desastre"),
    (desastre_tipo, "id_tipo_desastre"),
    (areas_afetadas, "id_desastre"),
):
    Index(f"ix_{tabela.name}_{coluna}", tabela.c[coluna])


def upgrade() -> None:
    for tabela in (tipos_desastre, desastres, desastre_tipo, areas_afetadas):
        op.execute(CreateTable(tabela))
        for indice in sorted(tabela.indexes, key=lambda i: i.name or ""):
            op.execute(CreateIndex(indice))


def downgrade() -> None:
    for nome in ("areas_afetadas", "desastre_tipo", "desastres", "tipos_desastre"):
        op.drop_table(nome)

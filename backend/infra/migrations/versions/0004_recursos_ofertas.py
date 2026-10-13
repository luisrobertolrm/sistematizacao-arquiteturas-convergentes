"""Tipos, recursos, ofertas e vínculos; snapshot independente do domínio.

Revision ID: 0004_recursos_ofertas
Revises: 0003_capacidades
"""

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
    text,
)
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.sql.schema import SchemaItem

revision: str = "0004_recursos_ofertas"
down_revision: str | None = "0003_capacidades"
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
for nome in ("instituicoes", "pessoas", "unidades_medida", "atividades"):
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


def responsavel() -> list[SchemaItem]:
    return [
        Column("instituicao_id", Uuid, ForeignKey("instituicoes.id", ondelete="RESTRICT")),
        Column("pessoa_id", Uuid, ForeignKey("pessoas.id", ondelete="RESTRICT")),
        CheckConstraint(
            "(instituicao_id IS NULL) <> (pessoa_id IS NULL)", name="responsavel_exclusivo"
        ),
    ]


tipos_recurso: Table = Table(
    "tipos_recurso",
    metadata,
    *auditoria(),
    Column("nome", String(200), nullable=False),
    Column("descricao", String(4000)),
    Column(
        "categoria",
        Enum(
            "veiculo",
            "equipamento",
            "material",
            "insumo",
            name="categoria_recurso",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column(
        "id_unidade_medida",
        Uuid,
        ForeignKey("unidades_medida.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column(
        "modo_controle",
        Enum(
            "individual",
            "estoque",
            name="modo_controle_recurso",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column("hash_conteudo_semantico", String(64), nullable=False),
    CheckConstraint("length(trim(nome)) >= 2", name="nome_obrigatorio"),
    CheckConstraint("hash_conteudo_semantico ~ '^[0-9a-f]{64}$'", name="hash_formato"),
)
recursos: Table = Table(
    "recursos",
    metadata,
    *auditoria(),
    *responsavel(),
    Column(
        "tipo_recurso_id", Uuid, ForeignKey("tipos_recurso.id", ondelete="RESTRICT"), nullable=False
    ),
    Column("nome", String(200), nullable=False),
    Column("descricao", String(4000)),
    Column("identificacao", String(200)),
    Column("quantidade_total", Numeric(18, 4), nullable=False),
    Column(
        "estado_operacional",
        Enum(
            "operacional",
            "em_manutencao",
            "indisponivel",
            name="estado_recurso",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column("municipio_codigo_ibge", String(7), nullable=False),
    Column("latitude", Numeric(10, 7)),
    Column("longitude", Numeric(10, 7)),
    CheckConstraint("length(trim(nome)) >= 2", name="nome_obrigatorio"),
    CheckConstraint("quantidade_total >= 0", name="quantidade_nao_negativa"),
    CheckConstraint("municipio_codigo_ibge ~ '^[0-9]{7}$'", name="municipio_formato"),
    CheckConstraint("(latitude IS NULL) = (longitude IS NULL)", name="coordenadas_pareadas"),
    CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude_limites"),
    CheckConstraint("longitude BETWEEN -180 AND 180", name="longitude_limites"),
)
ofertas_atividade: Table = Table(
    "ofertas_atividade",
    metadata,
    *auditoria(),
    *responsavel(),
    Column("atividade_id", Uuid, ForeignKey("atividades.id", ondelete="RESTRICT"), nullable=False),
    Column("municipio_atendimento_codigo_ibge", String(7), nullable=False),
    Column("descricao_complementar", String(4000)),
    Column("capacidade_declarada", Numeric(18, 4)),
    Column(
        "situacao_validacao",
        Enum(
            "pendente",
            "validada",
            "rejeitada",
            name="situacao_validacao_oferta",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    ),
    Column("validado_em", DateTime(timezone=True)),
    CheckConstraint("municipio_atendimento_codigo_ibge ~ '^[0-9]{7}$'", name="municipio_formato"),
    CheckConstraint("capacidade_declarada > 0", name="capacidade_positiva"),
    CheckConstraint(
        "(situacao_validacao = 'validada') = (validado_em IS NOT NULL)", name="validacao_data"
    ),
)
oferta_atividade_recurso: Table = Table(
    "oferta_atividade_recurso",
    metadata,
    *auditoria(),
    Column(
        "oferta_atividade_id",
        Uuid,
        ForeignKey("ofertas_atividade.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("recurso_id", Uuid, ForeignKey("recursos.id", ondelete="RESTRICT"), nullable=False),
    Column("quantidade_prevista", Numeric(18, 4), nullable=False),
    CheckConstraint("quantidade_prevista > 0", name="quantidade_positiva"),
)
for tabela in (tipos_recurso, recursos):
    Index(f"ix_{tabela.name}_nome_id", tabela.c.nome, tabela.c.id)
for tabela, colunas in (
    (tipos_recurso, ("id_unidade_medida",)),
    (recursos, ("tipo_recurso_id", "instituicao_id", "pessoa_id")),
    (ofertas_atividade, ("atividade_id", "instituicao_id", "pessoa_id")),
    (oferta_atividade_recurso, ("oferta_atividade_id", "recurso_id")),
):
    for coluna in colunas:
        Index(f"ix_{tabela.name}_{coluna}", tabela.c[coluna])
for dono in ("instituicao_id", "pessoa_id"):
    Index(
        f"uq_ofertas_atividade_ativa_{dono}",
        ofertas_atividade.c.atividade_id,
        ofertas_atividade.c[dono],
        ofertas_atividade.c.municipio_atendimento_codigo_ibge,
        unique=True,
        postgresql_where=text(f"inativado_em IS NULL AND {dono} IS NOT NULL"),
    )
Index(
    "uq_oferta_atividade_recurso_ativo",
    oferta_atividade_recurso.c.oferta_atividade_id,
    oferta_atividade_recurso.c.recurso_id,
    unique=True,
    postgresql_where=text("inativado_em IS NULL"),
)


def upgrade() -> None:
    for tabela in (tipos_recurso, recursos, ofertas_atividade, oferta_atividade_recurso):
        op.execute(CreateTable(tabela))
        for indice in sorted(tabela.indexes, key=lambda i: i.name or ""):
            op.execute(CreateIndex(indice))


def downgrade() -> None:
    for nome in ("oferta_atividade_recurso", "ofertas_atividade", "recursos", "tipos_recurso"):
        op.drop_table(nome)

"""Unidades, categorias, atividades e termos; snapshot independente.

Revision ID: 0003_capacidades
Revises: 0002_qualificacoes
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.schema import SchemaItem

revision: str = "0003_capacidades"
down_revision: str | None = "0002_qualificacoes"
branch_labels: str | None = None
depends_on: str | None = None


def auditoria() -> list[SchemaItem]:
    return [
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inativado_em", sa.DateTime(timezone=True)),
        sa.Column("criado_por", sa.String(200), nullable=False),
        sa.Column("atualizado_por", sa.String(200), nullable=False),
    ]


def catalogo(nome: str, *extras: SchemaItem) -> None:
    op.create_table(
        nome,
        *auditoria(),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.UniqueConstraint("codigo", name=op.f(f"uq_{nome}_codigo")),
        sa.CheckConstraint(
            "codigo ~ '^[a-z0-9][a-z0-9_-]{0,49}$'", name=op.f(f"ck_{nome}_codigo_formato")
        ),
        sa.CheckConstraint("length(trim(nome)) >= 2", name=op.f(f"ck_{nome}_nome_obrigatorio")),
        *extras,
    )
    op.create_index(f"ix_{nome}_nome_id", nome, ["nome", "id"])


def upgrade() -> None:
    catalogo(
        "unidades_medida",
        sa.Column("simbolo", sa.String(30), nullable=False),
        sa.CheckConstraint(
            "length(trim(simbolo)) >= 1", name=op.f("ck_unidades_medida_simbolo_obrigatorio")
        ),
    )
    catalogo("categorias_atividade", sa.Column("descricao", sa.String(4000)))
    catalogo(
        "atividades",
        sa.Column("descricao", sa.String(4000), nullable=False),
        sa.Column(
            "categoria_id",
            sa.Uuid(),
            sa.ForeignKey("categorias_atividade.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "id_unidade_capacidade",
            sa.Uuid(),
            sa.ForeignKey("unidades_medida.id", ondelete="RESTRICT"),
        ),
        sa.Column("orientacoes", sa.String(4000)),
        sa.Column("restricoes", sa.String(4000)),
        sa.Column("hash_conteudo_semantico", sa.String(64), nullable=False),
        sa.CheckConstraint(
            "length(trim(descricao)) >= 2", name=op.f("ck_atividades_descricao_obrigatoria")
        ),
        sa.CheckConstraint(
            "hash_conteudo_semantico ~ '^[0-9a-f]{64}$'", name=op.f("ck_atividades_hash_formato")
        ),
    )
    op.create_index("ix_atividades_categoria_id", "atividades", ["categoria_id"])
    op.create_index("ix_atividades_id_unidade_capacidade", "atividades", ["id_unidade_capacidade"])
    op.create_table(
        "atividade_termos",
        *auditoria(),
        sa.Column(
            "atividade_id",
            sa.Uuid(),
            sa.ForeignKey("atividades.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("termo", sa.String(200), nullable=False),
        sa.CheckConstraint(
            "length(trim(termo)) >= 2", name=op.f("ck_atividade_termos_termo_obrigatorio")
        ),
    )
    op.create_index("ix_atividade_termos_atividade_id", "atividade_termos", ["atividade_id"])
    op.create_index(
        "uq_atividade_termos_ativo",
        "atividade_termos",
        ["atividade_id", "termo"],
        unique=True,
        postgresql_where=sa.text("inativado_em IS NULL"),
    )


def downgrade() -> None:
    op.drop_table("atividade_termos")
    op.drop_table("atividades")
    op.drop_table("categorias_atividade")
    op.drop_table("unidades_medida")

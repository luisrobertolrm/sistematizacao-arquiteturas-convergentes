"""Instituições e pessoas: primeiro incremento, sem migrar automaticamente no startup.

Revision ID: 0001_cadastros
Revises: None
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.schema import SchemaItem

revision: str = "0001_cadastros"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def criar_contato(nome: str, institucional: bool) -> None:
    adicionais: list[SchemaItem] = []
    if institucional:
        adicionais = [
            sa.Column("razao_social", sa.String(200)),
            sa.Column("cnpj", sa.String(14)),
            sa.Column("descricao", sa.String(4000)),
            sa.Column(
                "tipo",
                sa.Enum(
                    "orgao_publico",
                    "empresa",
                    "ong",
                    "associacao",
                    name="tipo_instituicao",
                    native_enum=False,
                    create_constraint=True,
                ),
                nullable=False,
            ),
            sa.UniqueConstraint("cnpj", name="uq_instituicoes_cnpj"),
        ]
    op.create_table(
        nome,
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("municipio_codigo_ibge", sa.String(7), nullable=False),
        sa.Column("uf", sa.String(2), nullable=False),
        sa.Column(
            "situacao_cadastral",
            sa.Enum(
                "pendente",
                "validada",
                "rejeitada",
                name="situacao_cadastral",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("email_contato", sa.String(320)),
        sa.Column("telefone_contato", sa.String(16)),
        sa.Column("latitude", sa.Numeric(10, 7)),
        sa.Column("longitude", sa.Numeric(10, 7)),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inativado_em", sa.DateTime(timezone=True)),
        sa.Column("criado_por", sa.String(200), nullable=False),
        sa.Column("atualizado_por", sa.String(200), nullable=False),
        sa.CheckConstraint(
            "(latitude IS NULL) = (longitude IS NULL)", name=op.f(f"ck_{nome}_coordenadas_pareadas")
        ),
        sa.CheckConstraint("latitude BETWEEN -90 AND 90", name=op.f(f"ck_{nome}_latitude_valida")),
        sa.CheckConstraint(
            "longitude BETWEEN -180 AND 180", name=op.f(f"ck_{nome}_longitude_valida")
        ),
        sa.CheckConstraint("length(trim(nome)) > 0", name=op.f(f"ck_{nome}_nome_obrigatorio")),
        sa.CheckConstraint(
            "length(municipio_codigo_ibge) = 7", name=op.f(f"ck_{nome}_municipio_tamanho")
        ),
        sa.CheckConstraint("length(uf) = 2", name=op.f(f"ck_{nome}_uf_tamanho")),
        *adicionais,
    )
    op.create_index(f"ix_{nome}_nome_id", nome, ["nome", "id"])


def upgrade() -> None:
    criar_contato("instituicoes", True)
    criar_contato("pessoas", False)


def downgrade() -> None:
    op.drop_table("pessoas")
    op.drop_table("instituicoes")

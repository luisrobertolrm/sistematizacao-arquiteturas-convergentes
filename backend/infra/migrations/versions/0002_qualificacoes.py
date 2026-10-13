"""Catálogos e vínculos de pessoas; snapshot independente dos modelos atuais.

Revision ID: 0002_qualificacoes
Revises: 0001_cadastros
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.schema import SchemaItem

revision: str = "0002_qualificacoes"
down_revision: str | None = "0001_cadastros"
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


def dominio(nome: str, *valores: str) -> sa.Enum:
    return sa.Enum(*valores, native_enum=False, create_constraint=True, name=nome)


def catalogo(nome: str, *extras: SchemaItem) -> None:
    op.create_table(
        nome,
        *auditoria(),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.String(4000)),
        sa.Column("hash_conteudo_semantico", sa.String(64), nullable=False),
        sa.CheckConstraint("length(trim(nome)) >= 2", name=op.f(f"ck_{nome}_nome_obrigatorio")),
        sa.CheckConstraint(
            "hash_conteudo_semantico ~ '^[0-9a-f]{64}$'", name=op.f(f"ck_{nome}_hash_formato")
        ),
        *extras,
    )
    op.create_index(f"ix_{nome}_nome_id", nome, ["nome", "id"])


def vinculo(nome: str, coluna: str, destino: str, *extras: SchemaItem) -> None:
    op.create_table(
        nome,
        *auditoria(),
        sa.Column(
            "pessoa_id", sa.Uuid(), sa.ForeignKey("pessoas.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column(
            coluna, sa.Uuid(), sa.ForeignKey(f"{destino}.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column(
            "situacao_validacao",
            dominio("situacao_validacao", "pendente", "validada", "rejeitada"),
            nullable=False,
        ),
        *extras,
    )
    op.create_index(f"ix_{nome}_pessoa_id_criado_em", nome, ["pessoa_id", "criado_em", "id"])
    op.create_index(f"ix_{nome}_{coluna}", nome, [coluna])


def upgrade() -> None:
    catalogo(
        "profissoes",
        sa.Column("codigo_cbo", sa.String(6)),
        sa.CheckConstraint("codigo_cbo ~ '^[0-9]{6}$'", name=op.f("ck_profissoes_cbo_formato")),
    )
    catalogo(
        "cursos",
        sa.Column(
            "tipo", dominio("tipo_curso", "tecnico", "capacitacao", "treinamento"), nullable=False
        ),
    )
    vinculo(
        "pessoa_instituicao",
        "instituicao_id",
        "instituicoes",
        sa.Column(
            "tipo_vinculo",
            dominio("tipo_vinculo", "voluntario", "funcionario", "associado", "representante"),
            nullable=False,
        ),
        sa.Column("inicio_em", sa.Date(), nullable=False),
        sa.Column("fim_em", sa.Date()),
        sa.CheckConstraint(
            "fim_em IS NULL OR fim_em >= inicio_em",
            name=op.f("ck_pessoa_instituicao_periodo_valido"),
        ),
    )
    op.create_index(
        "uq_pessoa_instituicao_aberto",
        "pessoa_instituicao",
        ["pessoa_id", "instituicao_id", "tipo_vinculo"],
        unique=True,
        postgresql_where=sa.text("inativado_em IS NULL AND fim_em IS NULL"),
    )
    vinculo(
        "pessoa_profissao",
        "profissao_id",
        "profissoes",
        sa.Column("registro_profissional", sa.String(100)),
        sa.Column("orgao_registro", sa.String(100)),
        sa.Column("uf_registro", sa.String(2)),
        sa.Column("validade_em", sa.Date()),
        sa.CheckConstraint(
            "uf_registro IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT',"
            "'MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP',"
            "'SE','TO')",
            name=op.f("ck_pessoa_profissao_uf_registro_valida"),
        ),
    )
    op.create_index(
        "uq_pessoa_profissao_qualificacao",
        "pessoa_profissao",
        [
            "pessoa_id",
            "profissao_id",
            "registro_profissional",
            "orgao_registro",
            "uf_registro",
            "validade_em",
        ],
        unique=True,
        postgresql_nulls_not_distinct=True,
        postgresql_where=sa.text("inativado_em IS NULL"),
    )
    vinculo(
        "pessoa_curso",
        "curso_id",
        "cursos",
        sa.Column("instituicao_emissora", sa.String(200), nullable=False),
        sa.Column("conclusao_em", sa.Date(), nullable=False),
        sa.Column("validade_em", sa.Date()),
        sa.Column("carga_horaria", sa.Numeric(10, 2)),
        sa.Column("comprovante_referencia", sa.String(500)),
        sa.CheckConstraint(
            "length(trim(instituicao_emissora)) >= 2",
            name=op.f("ck_pessoa_curso_emissor_obrigatorio"),
        ),
        sa.CheckConstraint(
            "validade_em IS NULL OR validade_em >= conclusao_em",
            name=op.f("ck_pessoa_curso_validade_ordenada"),
        ),
        sa.CheckConstraint(
            "carga_horaria IS NULL OR carga_horaria > 0",
            name=op.f("ck_pessoa_curso_carga_positiva"),
        ),
    )
    op.create_index(
        "uq_pessoa_curso_conclusao",
        "pessoa_curso",
        ["pessoa_id", "curso_id", sa.text("lower(btrim(instituicao_emissora))"), "conclusao_em"],
        unique=True,
        postgresql_where=sa.text("inativado_em IS NULL"),
    )


def downgrade() -> None:
    for nome in ("pessoa_curso", "pessoa_profissao", "pessoa_instituicao", "cursos", "profissoes"):
        op.drop_table(nome)

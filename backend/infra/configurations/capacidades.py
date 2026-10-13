from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, Uuid, text
from sqlalchemy.sql.schema import SchemaItem

from core.entity.capacidades import Atividade, AtividadeTermo, CategoriaAtividade, UnidadeMedida
from infra.configurations.cadastros import mapeamentos, metadata
from infra.configurations.qualificacoes import auditoria


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


unidades_medida: Table = catalogo_codigo(
    "unidades_medida",
    Column("simbolo", String(30), nullable=False),
    CheckConstraint("length(trim(simbolo)) >= 1", name="simbolo_obrigatorio"),
)
categorias_atividade: Table = catalogo_codigo(
    "categorias_atividade", Column("descricao", String(4000))
)
atividades: Table = catalogo_codigo(
    "atividades",
    Column("descricao", String(4000), nullable=False),
    Column(
        "categoria_id",
        Uuid,
        ForeignKey("categorias_atividade.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("id_unidade_capacidade", Uuid, ForeignKey("unidades_medida.id", ondelete="RESTRICT")),
    Column("orientacoes", String(4000)),
    Column("restricoes", String(4000)),
    Column("hash_conteudo_semantico", String(64), nullable=False),
    CheckConstraint("length(trim(descricao)) >= 2", name="descricao_obrigatoria"),
    CheckConstraint("hash_conteudo_semantico ~ '^[0-9a-f]{64}$'", name="hash_formato"),
)
Index("ix_atividades_categoria_id", atividades.c.categoria_id)
Index("ix_atividades_id_unidade_capacidade", atividades.c.id_unidade_capacidade)
atividade_termos: Table = Table(
    "atividade_termos",
    metadata,
    *auditoria(),
    Column("atividade_id", Uuid, ForeignKey("atividades.id", ondelete="RESTRICT"), nullable=False),
    Column("termo", String(200), nullable=False),
    CheckConstraint("length(trim(termo)) >= 2", name="termo_obrigatorio"),
)
Index("ix_atividade_termos_atividade_id", atividade_termos.c.atividade_id)
Index(
    "uq_atividade_termos_ativo",
    atividade_termos.c.atividade_id,
    atividade_termos.c.termo,
    unique=True,
    postgresql_where=text("inativado_em IS NULL"),
)

mapeamentos.map_imperatively(UnidadeMedida, unidades_medida)
mapeamentos.map_imperatively(CategoriaAtividade, categorias_atividade)
mapeamentos.map_imperatively(Atividade, atividades)
mapeamentos.map_imperatively(AtividadeTermo, atividade_termos)

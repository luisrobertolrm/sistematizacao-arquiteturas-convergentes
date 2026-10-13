from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Table,
    Uuid,
    func,
    text,
)
from sqlalchemy.sql.schema import SchemaItem

from core.entity.qualificacoes import (
    Curso,
    PessoaCurso,
    PessoaInstituicao,
    PessoaProfissao,
    Profissao,
    SituacaoValidacao,
    TipoCurso,
    TipoVinculo,
)
from infra.configurations.cadastros import mapeamentos, metadata


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


def catalogo(nome: str, *adicionais: SchemaItem) -> Table:
    tabela: Table = Table(
        nome,
        metadata,
        *auditoria(),
        Column("nome", String(200), nullable=False),
        Column("descricao", String(4000)),
        Column("hash_conteudo_semantico", String(64), nullable=False),
        CheckConstraint("length(trim(nome)) >= 2", name="nome_obrigatorio"),
        CheckConstraint("hash_conteudo_semantico ~ '^[0-9a-f]{64}$'", name="hash_formato"),
        *adicionais,
    )
    Index(f"ix_{nome}_nome_id", tabela.c.nome, tabela.c.id)
    return tabela


profissoes: Table = catalogo(
    "profissoes",
    Column("codigo_cbo", String(6)),
    CheckConstraint("codigo_cbo ~ '^[0-9]{6}$'", name="cbo_formato"),
)
cursos: Table = catalogo(
    "cursos",
    Column("tipo", enum_tipo(TipoCurso, "tipo_curso"), nullable=False),
)


def vinculo(nome: str, referencia: str, destino: str, *adicionais: SchemaItem) -> Table:
    tabela: Table = Table(
        nome,
        metadata,
        *auditoria(),
        Column("pessoa_id", Uuid, ForeignKey("pessoas.id", ondelete="RESTRICT"), nullable=False),
        Column(referencia, Uuid, ForeignKey(f"{destino}.id", ondelete="RESTRICT"), nullable=False),
        Column(
            "situacao_validacao", enum_tipo(SituacaoValidacao, "situacao_validacao"), nullable=False
        ),
        *adicionais,
    )
    Index(f"ix_{nome}_pessoa_id_criado_em", tabela.c.pessoa_id, tabela.c.criado_em, tabela.c.id)
    Index(f"ix_{nome}_{referencia}", tabela.c[referencia])
    return tabela


pessoa_instituicao: Table = vinculo(
    "pessoa_instituicao",
    "instituicao_id",
    "instituicoes",
    Column("tipo_vinculo", enum_tipo(TipoVinculo, "tipo_vinculo"), nullable=False),
    Column("inicio_em", Date, nullable=False),
    Column("fim_em", Date),
    CheckConstraint("fim_em IS NULL OR fim_em >= inicio_em", name="periodo_valido"),
)
Index(
    "uq_pessoa_instituicao_aberto",
    pessoa_instituicao.c.pessoa_id,
    pessoa_instituicao.c.instituicao_id,
    pessoa_instituicao.c.tipo_vinculo,
    unique=True,
    postgresql_where=text("inativado_em IS NULL AND fim_em IS NULL"),
)

pessoa_profissao: Table = vinculo(
    "pessoa_profissao",
    "profissao_id",
    "profissoes",
    Column("registro_profissional", String(100)),
    Column("orgao_registro", String(100)),
    Column("uf_registro", String(2)),
    Column("validade_em", Date),
    CheckConstraint(
        "uf_registro IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT',"
        "'MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO')",
        name="uf_registro_valida",
    ),
)
Index(
    "uq_pessoa_profissao_qualificacao",
    pessoa_profissao.c.pessoa_id,
    pessoa_profissao.c.profissao_id,
    pessoa_profissao.c.registro_profissional,
    pessoa_profissao.c.orgao_registro,
    pessoa_profissao.c.uf_registro,
    pessoa_profissao.c.validade_em,
    unique=True,
    postgresql_nulls_not_distinct=True,
    postgresql_where=text("inativado_em IS NULL"),
)

pessoa_curso: Table = vinculo(
    "pessoa_curso",
    "curso_id",
    "cursos",
    Column("instituicao_emissora", String(200), nullable=False),
    Column("conclusao_em", Date, nullable=False),
    Column("validade_em", Date),
    Column("carga_horaria", Numeric(10, 2)),
    Column("comprovante_referencia", String(500)),
    CheckConstraint("length(trim(instituicao_emissora)) >= 2", name="emissor_obrigatorio"),
    CheckConstraint("validade_em IS NULL OR validade_em >= conclusao_em", name="validade_ordenada"),
    CheckConstraint("carga_horaria IS NULL OR carga_horaria > 0", name="carga_positiva"),
)
Index(
    "uq_pessoa_curso_conclusao",
    pessoa_curso.c.pessoa_id,
    pessoa_curso.c.curso_id,
    func.lower(func.btrim(pessoa_curso.c.instituicao_emissora)),
    pessoa_curso.c.conclusao_em,
    unique=True,
    postgresql_where=text("inativado_em IS NULL"),
)

mapeamentos.map_imperatively(Profissao, profissoes)
mapeamentos.map_imperatively(Curso, cursos)
mapeamentos.map_imperatively(PessoaInstituicao, pessoa_instituicao)
mapeamentos.map_imperatively(PessoaProfissao, pessoa_profissao)
mapeamentos.map_imperatively(PessoaCurso, pessoa_curso)

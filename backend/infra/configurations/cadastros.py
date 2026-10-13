from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Index,
    MetaData,
    Numeric,
    String,
    Table,
    Uuid,
)
from sqlalchemy.orm import registry

from core.entity.cadastros import Instituicao, Pessoa, SituacaoCadastral, TipoInstituicao

metadata: MetaData = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
mapeamentos: registry = registry(metadata=metadata)


def tabela_contato(nome: str, institucional: bool) -> Table:
    tabela: Table = Table(
        nome,
        metadata,
        Column("id", Uuid, primary_key=True),
        Column("nome", String(200), nullable=False),
        Column("municipio_codigo_ibge", String(7), nullable=False),
        Column("uf", String(2), nullable=False),
        Column(
            "situacao_cadastral",
            Enum(
                SituacaoCadastral,
                native_enum=False,
                create_constraint=True,
                name="situacao_cadastral",
                values_callable=lambda e: [str(v.value) for v in e],
            ),
            nullable=False,
        ),
        Column("email_contato", String(320)),
        Column("telefone_contato", String(16)),
        Column("latitude", Numeric(10, 7)),
        Column("longitude", Numeric(10, 7)),
        Column("criado_em", DateTime(timezone=True), nullable=False),
        Column("atualizado_em", DateTime(timezone=True), nullable=False),
        Column("inativado_em", DateTime(timezone=True)),
        Column("criado_por", String(200), nullable=False),
        Column("atualizado_por", String(200), nullable=False),
        CheckConstraint("(latitude IS NULL) = (longitude IS NULL)", name="coordenadas_pareadas"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude_valida"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="longitude_valida"),
        CheckConstraint("length(trim(nome)) > 0", name="nome_obrigatorio"),
        CheckConstraint("length(municipio_codigo_ibge) = 7", name="municipio_tamanho"),
        CheckConstraint("length(uf) = 2", name="uf_tamanho"),
    )
    if institucional:
        tabela.append_column(Column("razao_social", String(200)))
        tabela.append_column(Column("cnpj", String(14), unique=True))
        tabela.append_column(Column("descricao", String(4000)))
        tabela.append_column(
            Column(
                "tipo",
                Enum(
                    TipoInstituicao,
                    native_enum=False,
                    create_constraint=True,
                    name="tipo_instituicao",
                    values_callable=lambda e: [str(v.value) for v in e],
                ),
                nullable=False,
            )
        )
    Index(f"ix_{nome}_nome_id", tabela.c.nome, tabela.c.id)
    return tabela


instituicoes: Table = tabela_contato("instituicoes", True)
pessoas: Table = tabela_contato("pessoas", False)
mapeamentos.map_imperatively(Instituicao, instituicoes)
mapeamentos.map_imperatively(Pessoa, pessoas)

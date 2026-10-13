from pydantic import TypeAdapter
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from core.entity.desastres import (
    AreaAfetada,
    Desastre,
    DesastreTipo,
    GravidadeArea,
    SituacaoArea,
    SituacaoDesastre,
    TipoDesastre,
)
from core.geometria import GeometriaArea, GeometriaJSON
from infra.configurations.cadastros import mapeamentos, metadata
from infra.configurations.capacidades import catalogo_codigo
from infra.configurations.qualificacoes import auditoria, enum_tipo


class GeometriaTipo(TypeDecorator[GeometriaArea]):
    impl = JSONB
    cache_ok = True

    def process_bind_param(
        self, value: GeometriaArea | None, dialect: Dialect
    ) -> GeometriaJSON | None:
        return value.para_json() if value is not None else None

    def process_result_value(self, value: object, dialect: Dialect) -> GeometriaArea | None:
        return (
            GeometriaArea.de_json(TypeAdapter(GeometriaJSON).validate_python(value))
            if value is not None
            else None
        )


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
    Column("situacao", enum_tipo(SituacaoDesastre, "situacao_desastre"), nullable=False),
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
    Column("geometria", GeometriaTipo(), nullable=False),
    Column("gravidade", enum_tipo(GravidadeArea, "gravidade_area"), nullable=False),
    Column("situacao", enum_tipo(SituacaoArea, "situacao_area"), nullable=False),
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
mapeamentos.map_imperatively(TipoDesastre, tipos_desastre)
mapeamentos.map_imperatively(Desastre, desastres)
mapeamentos.map_imperatively(DesastreTipo, desastre_tipo)
mapeamentos.map_imperatively(AreaAfetada, areas_afetadas)

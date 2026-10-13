from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Table,
    Uuid,
)

from core.entity.operacao import Demanda, DemandaItem, PrioridadeDemanda, SituacaoDemanda
from infra.configurations.cadastros import mapeamentos, metadata
from infra.configurations.qualificacoes import auditoria, enum_tipo

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
mapeamentos.map_imperatively(Demanda, demandas)
mapeamentos.map_imperatively(DemandaItem, demanda_itens)

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB

from core.entity.operacao import (
    Recomendacao,
    RecomendacaoInstituicao,
    RecomendacaoItem,
    RecomendacaoPessoa,
    RecomendacaoRecurso,
    SituacaoRecomendacao,
)
from infra.configurations.cadastros import mapeamentos, metadata
from infra.configurations.qualificacoes import auditoria, enum_tipo

recomendacoes = Table(
    "recomendacoes",
    metadata,
    *auditoria(),
    Column("id_demanda", Uuid, ForeignKey("demandas.id"), nullable=False),
    Column("id_modelo_embedding", Uuid, ForeignKey("modelo_ia.id"), nullable=False),
    Column("id_modelo_inferencia", Uuid, ForeignKey("modelo_ia.id"), nullable=False),
    Column("hash_contexto", String(64), nullable=False),
    Column("gerada_em", DateTime(timezone=True), nullable=False),
    Column("justificativa", String(4000), nullable=False),
    Column("pendencias", JSONB, nullable=False),
    Column("situacao", enum_tipo(SituacaoRecomendacao, "situacao_recomendacao"), nullable=False),
    Column("decidida_em", DateTime(timezone=True)),
    Column("decidida_por", String(200)),
    Column("justificativa_decisao", String(4000)),
    CheckConstraint(
        "(situacao = 'gerada' AND decidida_em IS NULL AND decidida_por IS NULL "
        "AND justificativa_decisao IS NULL) OR (situacao IN ('aprovada', 'rejeitada') "
        "AND decidida_em IS NOT NULL AND decidida_por IS NOT NULL "
        "AND justificativa_decisao IS NOT NULL)",
        name="decisao_coerente",
    ),
)
recomendacao_itens = Table(
    "recomendacao_itens",
    metadata,
    *auditoria(),
    Column("id_recomendacao", Uuid, ForeignKey("recomendacoes.id"), nullable=False),
    Column("id_demanda_item", Uuid, ForeignKey("demanda_itens.id"), nullable=False),
    Column("quantidade_sugerida", Numeric(18, 4), nullable=False),
    Column("justificativa", String(4000), nullable=False),
    CheckConstraint("quantidade_sugerida >= 0", name="quantidade_nao_negativa"),
    UniqueConstraint("id_recomendacao", "id_demanda_item"),
)
recomendacao_pessoas = Table(
    "recomendacao_pessoas",
    metadata,
    *auditoria(),
    Column("id_recomendacao_item", Uuid, ForeignKey("recomendacao_itens.id"), nullable=False),
    Column("id_pessoa", Uuid, ForeignKey("pessoas.id"), nullable=False),
    Column("id_oferta_atividade", Uuid, ForeignKey("ofertas_atividade.id"), nullable=False),
    Column("papel_sugerido", String(200), nullable=False),
    UniqueConstraint("id_recomendacao_item", "id_pessoa"),
)
recomendacao_instituicoes = Table(
    "recomendacao_instituicoes",
    metadata,
    *auditoria(),
    Column("id_recomendacao_item", Uuid, ForeignKey("recomendacao_itens.id"), nullable=False),
    Column("id_instituicao", Uuid, ForeignKey("instituicoes.id"), nullable=False),
    Column("id_oferta_atividade", Uuid, ForeignKey("ofertas_atividade.id"), nullable=False),
    UniqueConstraint("id_recomendacao_item", "id_oferta_atividade"),
)
recomendacao_recursos = Table(
    "recomendacao_recursos",
    metadata,
    *auditoria(),
    Column("id_recomendacao_item", Uuid, ForeignKey("recomendacao_itens.id"), nullable=False),
    Column("id_recurso", Uuid, ForeignKey("recursos.id"), nullable=False),
    Column("quantidade_sugerida", Numeric(18, 4), nullable=False),
    CheckConstraint("quantidade_sugerida > 0", name="quantidade_positiva"),
    UniqueConstraint("id_recomendacao_item", "id_recurso"),
)
for tabela in (
    recomendacoes,
    recomendacao_itens,
    recomendacao_pessoas,
    recomendacao_instituicoes,
    recomendacao_recursos,
):
    for coluna in tabela.c:
        if coluna.foreign_keys:
            Index(f"ix_{tabela.name}_{coluna.name}", coluna)
mapeamentos.map_imperatively(Recomendacao, recomendacoes)
mapeamentos.map_imperatively(RecomendacaoItem, recomendacao_itens)
mapeamentos.map_imperatively(RecomendacaoPessoa, recomendacao_pessoas)
mapeamentos.map_imperatively(RecomendacaoInstituicao, recomendacao_instituicoes)
mapeamentos.map_imperatively(RecomendacaoRecurso, recomendacao_recursos)

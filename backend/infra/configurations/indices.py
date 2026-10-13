from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Double,
    ForeignKey,
    Index,
    String,
    Table,
    Uuid,
)
from sqlalchemy.dialects.postgresql import ARRAY

from core.entity.operacao import AtividadeIndiceSemantico, SituacaoIndexacao
from infra.configurations.cadastros import mapeamentos, metadata
from infra.configurations.qualificacoes import auditoria, enum_tipo

atividade_indice_semantico = Table(
    "atividade_indice_semantico",
    metadata,
    *auditoria(),
    Column("id_atividade", Uuid, ForeignKey("atividades.id"), nullable=False),
    Column("id_modelo", Uuid, ForeignKey("modelo_ia.id"), nullable=False),
    Column("hash_atividade_origem", String(64), nullable=False),
    Column("embedding", ARRAY(Double)),
    Column(
        "situacao_indexacao", enum_tipo(SituacaoIndexacao, "situacao_indexacao"), nullable=False
    ),
    Column("indexado_em", DateTime(timezone=True)),
    CheckConstraint(
        "(situacao_indexacao = 'pronta' AND embedding IS NOT NULL AND indexado_em IS NOT NULL) "
        "OR (situacao_indexacao = 'pendente' AND embedding IS NULL)",
        name="estado_vetor_coerente",
    ),
)
Index(
    "uq_atividade_indice_par",
    atividade_indice_semantico.c.id_atividade,
    atividade_indice_semantico.c.id_modelo,
    unique=True,
)
Index("ix_atividade_indice_semantico_id_modelo", atividade_indice_semantico.c.id_modelo)
mapeamentos.map_imperatively(AtividadeIndiceSemantico, atividade_indice_semantico)

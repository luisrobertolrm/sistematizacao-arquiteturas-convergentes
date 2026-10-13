from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Table,
    Uuid,
    text,
)

from core.entity.operacao import ConexaoIA, FinalidadeModeloIA, ModeloIA, TipoAutenticacaoIA
from infra.configurations.cadastros import mapeamentos, metadata
from infra.configurations.qualificacoes import auditoria, enum_tipo

conexao_ia = Table(
    "conexao_ia",
    metadata,
    *auditoria(),
    Column("nome", String(200), nullable=False),
    Column("provedor", String(50), nullable=False),
    Column("url_base", String(2000), nullable=False),
    Column("tipo_autenticacao", enum_tipo(TipoAutenticacaoIA, "autenticacao_ia"), nullable=False),
    Column("token_criptografado", LargeBinary),
    Column("identificador_chave", String(100)),
    CheckConstraint("provedor = 'openai_compativel'", name="provedor_suportado"),
    CheckConstraint(
        "(tipo_autenticacao = 'bearer' AND token_criptografado IS NOT NULL "
        "AND identificador_chave IS NOT NULL) OR (tipo_autenticacao = 'nenhuma' "
        "AND token_criptografado IS NULL AND identificador_chave IS NULL)",
        name="credencial_coerente",
    ),
)
modelo_ia = Table(
    "modelo_ia",
    metadata,
    *auditoria(),
    Column("id_conexao", Uuid, ForeignKey("conexao_ia.id"), nullable=False),
    Column("identificador_modelo", String(200), nullable=False),
    Column("revisao", String(200)),
    Column("finalidade", enum_tipo(FinalidadeModeloIA, "finalidade_modelo"), nullable=False),
    Column("dimensao", Integer),
    Column("ativo", Boolean, nullable=False),
    CheckConstraint(
        "(finalidade = 'embedding' AND dimensao IS NOT NULL AND dimensao BETWEEN 1 AND 16384) OR "
        "(finalidade = 'inferencia_texto' AND dimensao IS NULL)",
        name="dimensao_coerente",
    ),
    CheckConstraint("NOT ativo OR inativado_em IS NULL", name="ativo_vigente"),
)
Index(
    "uq_modelo_ia_finalidade_ativa",
    modelo_ia.c.finalidade,
    unique=True,
    postgresql_where=text("ativo AND inativado_em IS NULL"),
)
Index("ix_modelo_ia_id_conexao", modelo_ia.c.id_conexao)
mapeamentos.map_imperatively(ConexaoIA, conexao_ia)
mapeamentos.map_imperatively(ModeloIA, modelo_ia)

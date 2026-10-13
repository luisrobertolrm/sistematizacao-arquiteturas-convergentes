"""Recortes tipados do modelo lógico D001–D009 para exercício em memória.

Não são entidades de produção. Auditoria comum e diversos campos opcionais são
omitidos. Escalas de prioridade/gravidade e detalhes da recomendação são
convenções do cenário, sem aprovar contratos ainda pendentes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
from uuid import UUID


class Validacao(StrEnum):
    VALIDADA = "validada"
    PENDENTE = "pendente"
    REJEITADA = "rejeitada"


class Finalidade(StrEnum):
    EMBEDDING = "embedding"
    TEXTO = "inferencia_texto"


class SituacaoRecomendacao(StrEnum):
    GERADA = "gerada"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"


@dataclass(frozen=True, slots=True)
class Instituicao:
    id: UUID
    nome: str
    municipio_codigo_ibge: str
    situacao_cadastral: Validacao


@dataclass(frozen=True, slots=True)
class Pessoa:
    id: UUID
    nome: str
    municipio_codigo_ibge: str
    situacao_cadastral: Validacao


@dataclass(frozen=True, slots=True)
class PessoaInstituicao:
    pessoa_id: UUID
    instituicao_id: UUID
    inicio_em: date
    fim_em: date | None
    situacao_validacao: Validacao


@dataclass(frozen=True, slots=True)
class Profissao:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class PessoaProfissao:
    pessoa_id: UUID
    profissao_id: UUID
    situacao_validacao: Validacao


@dataclass(frozen=True, slots=True)
class Curso:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class PessoaCurso:
    pessoa_id: UUID
    curso_id: UUID
    conclusao_em: date
    validade_em: date | None
    situacao_validacao: Validacao


@dataclass(frozen=True, slots=True)
class UnidadeMedida:
    id: UUID
    codigo: str
    nome: str


@dataclass(frozen=True, slots=True)
class CategoriaAtividade:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class Atividade:
    id: UUID
    codigo: str
    nome: str
    descricao: str
    categoria_id: UUID
    id_unidade_capacidade: UUID

    @property
    def hash_conteudo_semantico(self) -> str:
        # Apenas para este exercício; serialização canônica final ainda pendente.
        conteudo: str = "\x1f".join((
            self.codigo, self.nome, self.descricao,
            str(self.categoria_id), str(self.id_unidade_capacidade),
        ))
        return sha256(conteudo.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AtividadeTermo:
    atividade_id: UUID
    termo: str


@dataclass(frozen=True, slots=True)
class OfertaAtividade:
    id: UUID
    atividade_id: UUID
    instituicao_id: UUID | None
    pessoa_id: UUID | None
    capacidade_declarada: Decimal
    municipio_atendimento_codigo_ibge: str
    situacao_validacao: Validacao


@dataclass(frozen=True, slots=True)
class OfertaAtividadeRecurso:
    oferta_atividade_id: UUID
    recurso_id: UUID
    quantidade_prevista: Decimal


@dataclass(frozen=True, slots=True)
class TipoRecurso:
    id: UUID
    nome: str
    id_unidade_medida: UUID
    modo_controle: str


@dataclass(frozen=True, slots=True)
class Recurso:
    id: UUID
    tipo_recurso_id: UUID
    nome: str
    descricao: str
    instituicao_id: UUID | None
    pessoa_id: UUID | None
    quantidade_total: Decimal
    estado_operacional: str
    municipio_codigo_ibge: str


@dataclass(frozen=True, slots=True)
class TipoDesastre:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class Desastre:
    id: UUID
    titulo: str
    inicio_em: datetime
    situacao: str
    id_instituicao_coordenadora: UUID


@dataclass(frozen=True, slots=True)
class DesastreTipo:
    id_desastre: UUID
    id_tipo_desastre: UUID
    principal: bool


@dataclass(frozen=True, slots=True)
class Coordenada:
    longitude: Decimal
    latitude: Decimal


@dataclass(frozen=True, slots=True)
class AreaAfetada:
    id: UUID
    id_desastre: UUID
    nome: str
    municipio_codigo_ibge: str
    geometria: tuple[Coordenada, ...]
    gravidade: str
    ultima_avaliacao_em: datetime


@dataclass(frozen=True, slots=True)
class Demanda:
    id: UUID
    id_area_afetada: UUID
    titulo: str
    prioridade: str
    inicio_previsto_em: datetime
    prazo_em: datetime
    id_pessoa_solicitante: UUID
    situacao: str


@dataclass(frozen=True, slots=True)
class DemandaItem:
    id: UUID
    id_demanda: UUID
    id_atividade: UUID | None
    id_tipo_recurso: UUID | None
    quantidade_solicitada: Decimal
    id_unidade_medida: UUID
    observacoes: str | None


@dataclass(frozen=True, slots=True)
class ConexaoIA:
    id: UUID
    nome: str
    provedor: str
    url_base: str
    tipo_autenticacao: str
    token_criptografado: bytes | None
    identificador_chave: str | None


@dataclass(frozen=True, slots=True)
class ModeloIA:
    id: UUID
    id_conexao: UUID
    identificador_modelo: str
    finalidade: Finalidade
    ativo: bool
    dimensao: int | None


@dataclass(frozen=True, slots=True)
class IndiceAtividade:
    id_atividade: UUID
    id_modelo: UUID
    embedding: tuple[float, ...] | None
    hash_atividade_origem: str
    situacao_indexacao: str


@dataclass(frozen=True, slots=True)
class Recomendacao:
    id: UUID
    id_demanda: UUID
    id_modelo_embedding: UUID
    id_modelo_inferencia: UUID
    gerada_em: datetime
    justificativa: str
    situacao: SituacaoRecomendacao


@dataclass(frozen=True, slots=True)
class RecomendacaoItem:
    id: UUID
    id_recomendacao: UUID
    id_demanda_item: UUID
    quantidade_sugerida: Decimal


@dataclass(frozen=True, slots=True)
class RecomendacaoPessoa:
    id_recomendacao_item: UUID
    id_pessoa: UUID
    id_oferta_atividade: UUID | None
    papel_sugerido: str


@dataclass(frozen=True, slots=True)
class RecomendacaoInstituicao:
    id_recomendacao_item: UUID
    id_instituicao: UUID
    id_oferta_atividade: UUID


@dataclass(frozen=True, slots=True)
class RecomendacaoRecurso:
    id_recomendacao_item: UUID
    id_recurso: UUID
    quantidade_sugerida: Decimal


@dataclass(frozen=True, slots=True)
class Sugestao:
    """Agregado auxiliar, não tabela adicional."""

    cabecalho: Recomendacao
    itens: tuple[RecomendacaoItem, ...]
    pessoas: tuple[RecomendacaoPessoa, ...]
    instituicoes: tuple[RecomendacaoInstituicao, ...]
    recursos: tuple[RecomendacaoRecurso, ...]
    pendencias: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AdministradorSimulado:
    """Identidade de teste; não define a futura tabela de usuários ou JWT."""

    identificador: str
    autorizado: bool


@dataclass(frozen=True, slots=True)
class DecisaoSimulada:
    """Evento auxiliar; esquema físico da auditoria administrativa está pendente."""

    id_recomendacao: UUID
    administrador: str
    situacao: SituacaoRecomendacao
    decidida_em: datetime
    motivo: str


@dataclass(frozen=True, slots=True)
class Cenario:
    instante: datetime
    instituicoes: dict[UUID, Instituicao]
    pessoas: dict[UUID, Pessoa]
    pessoa_instituicao: tuple[PessoaInstituicao, ...]
    profissoes: dict[UUID, Profissao]
    pessoa_profissao: tuple[PessoaProfissao, ...]
    cursos: dict[UUID, Curso]
    pessoa_curso: tuple[PessoaCurso, ...]
    unidades_medida: dict[UUID, UnidadeMedida]
    categorias_atividade: dict[UUID, CategoriaAtividade]
    atividades: dict[UUID, Atividade]
    atividade_termos: tuple[AtividadeTermo, ...]
    ofertas_atividade: dict[UUID, OfertaAtividade]
    oferta_atividade_recurso: tuple[OfertaAtividadeRecurso, ...]
    tipos_recurso: dict[UUID, TipoRecurso]
    recursos: dict[UUID, Recurso]
    tipos_desastre: dict[UUID, TipoDesastre]
    desastre: Desastre
    desastre_tipo: tuple[DesastreTipo, ...]
    areas_afetadas: dict[UUID, AreaAfetada]
    demandas: dict[UUID, Demanda]
    demanda_itens: dict[UUID, DemandaItem]
    conexoes: dict[UUID, ConexaoIA]
    modelos: dict[UUID, ModeloIA]
    indices: tuple[IndiceAtividade, ...]
    id_curso_filtro_demo: UUID

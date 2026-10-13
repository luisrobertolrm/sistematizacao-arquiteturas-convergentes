from dataclasses import dataclass
from uuid import UUID

from core.entity.cadastros import Entidade


@dataclass(kw_only=True)
class CatalogoComCodigo(Entidade):
    codigo: str
    nome: str


@dataclass(kw_only=True)
class UnidadeMedida(CatalogoComCodigo):
    simbolo: str


@dataclass(kw_only=True)
class CategoriaAtividade(CatalogoComCodigo):
    descricao: str | None = None


@dataclass(kw_only=True)
class Atividade(CatalogoComCodigo):
    descricao: str
    categoria_id: UUID
    id_unidade_capacidade: UUID | None = None
    orientacoes: str | None = None
    restricoes: str | None = None
    hash_conteudo_semantico: str


@dataclass(kw_only=True)
class AtividadeTermo(Entidade):
    atividade_id: UUID
    termo: str

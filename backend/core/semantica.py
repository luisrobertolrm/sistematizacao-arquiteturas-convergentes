"""Contrato canônico v1 dos catálogos; sem texto duplicado em índices."""

import json
from hashlib import sha256
from typing import TypedDict

from core.entity.capacidades import Atividade
from core.entity.qualificacoes import Curso, Profissao
from core.entity.recursos import TipoRecurso


class ConteudoTipoRecurso(TypedDict):
    versao: int
    catalogo: str
    nome: str
    descricao: str | None
    categoria: str


def hash_tipo_recurso(entidade: TipoRecurso) -> str:
    conteudo: ConteudoTipoRecurso = {
        "versao": 1,
        "catalogo": "tipos_recurso",
        "nome": entidade.nome,
        "descricao": entidade.descricao,
        "categoria": entidade.categoria.value,
    }
    canonico: str = json.dumps(
        conteudo, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return sha256(canonico.encode("utf-8")).hexdigest()


class ConteudoProfissao(TypedDict):
    versao: int
    catalogo: str
    nome: str
    descricao: str | None
    codigo_cbo: str | None


class ConteudoCurso(TypedDict):
    versao: int
    catalogo: str
    nome: str
    descricao: str | None
    tipo: str


class ConteudoAtividade(TypedDict):
    versao: int
    catalogo: str
    codigo: str
    nome: str
    descricao: str
    orientacoes: str | None
    restricoes: str | None
    termos: list[str]


def conteudo_atividade(entidade: Atividade, termos: list[str]) -> str:
    """Entrada semântica v1, sem nomes de referências ou campos de auditoria."""
    conteudo: ConteudoAtividade = {
        "versao": 1,
        "catalogo": "atividades",
        "codigo": entidade.codigo,
        "nome": entidade.nome,
        "descricao": entidade.descricao,
        "orientacoes": entidade.orientacoes,
        "restricoes": entidade.restricoes,
        "termos": sorted(set(termos)),
    }
    return json.dumps(
        conteudo, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def hash_atividade(entidade: Atividade, termos: list[str]) -> str:
    return sha256(conteudo_atividade(entidade, termos).encode("utf-8")).hexdigest()


def hash_qualificacao(entidade: Profissao | Curso) -> str:
    conteudo: ConteudoProfissao | ConteudoCurso
    if isinstance(entidade, Profissao):
        conteudo = ConteudoProfissao(
            versao=1,
            catalogo="profissoes",
            nome=entidade.nome,
            descricao=entidade.descricao,
            codigo_cbo=entidade.codigo_cbo,
        )
    else:
        conteudo = ConteudoCurso(
            versao=1,
            catalogo="cursos",
            nome=entidade.nome,
            descricao=entidade.descricao,
            tipo=entidade.tipo.value,
        )
    canonico: str = json.dumps(
        conteudo, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return sha256(canonico.encode("utf-8")).hexdigest()

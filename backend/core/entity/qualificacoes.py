from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from core.entity.cadastros import Entidade


class SituacaoValidacao(StrEnum):
    PENDENTE = "pendente"
    VALIDADA = "validada"
    REJEITADA = "rejeitada"


class TipoVinculo(StrEnum):
    VOLUNTARIO = "voluntario"
    FUNCIONARIO = "funcionario"
    ASSOCIADO = "associado"
    REPRESENTANTE = "representante"


class TipoCurso(StrEnum):
    TECNICO = "tecnico"
    CAPACITACAO = "capacitacao"
    TREINAMENTO = "treinamento"


@dataclass(kw_only=True)
class CatalogoQualificacao(Entidade):
    nome: str
    descricao: str | None = None
    hash_conteudo_semantico: str


@dataclass(kw_only=True)
class Profissao(CatalogoQualificacao):
    codigo_cbo: str | None = None


@dataclass(kw_only=True)
class Curso(CatalogoQualificacao):
    tipo: TipoCurso


@dataclass(kw_only=True)
class VinculoPessoa(Entidade):
    pessoa_id: UUID
    situacao_validacao: SituacaoValidacao = SituacaoValidacao.PENDENTE

    @property
    def id_referencia(self) -> UUID:
        raise NotImplementedError


@dataclass(kw_only=True)
class PessoaInstituicao(VinculoPessoa):
    instituicao_id: UUID
    tipo_vinculo: TipoVinculo
    inicio_em: date
    fim_em: date | None = None

    @property
    def id_referencia(self) -> UUID:
        return self.instituicao_id


@dataclass(kw_only=True)
class PessoaProfissao(VinculoPessoa):
    profissao_id: UUID
    registro_profissional: str | None = None
    orgao_registro: str | None = None
    uf_registro: str | None = None
    validade_em: date | None = None

    @property
    def id_referencia(self) -> UUID:
        return self.profissao_id


@dataclass(kw_only=True)
class PessoaCurso(VinculoPessoa):
    curso_id: UUID
    instituicao_emissora: str
    conclusao_em: date
    validade_em: date | None = None
    carga_horaria: Decimal | None = None
    comprovante_referencia: str | None = None

    @property
    def id_referencia(self) -> UUID:
        return self.curso_id

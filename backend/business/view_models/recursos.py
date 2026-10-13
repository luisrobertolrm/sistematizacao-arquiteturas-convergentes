from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from business.view_models.cadastros import AuditoriaVM
from business.view_models.qualificacoes import Entrada
from core.entity.qualificacoes import SituacaoValidacao
from core.entity.recursos import CategoriaRecurso, EstadoRecurso, ModoControleRecurso


class TipoRecursoInput(Entrada):
    nome: str = Field(min_length=2, max_length=200)
    descricao: str | None = Field(default=None, max_length=4000)
    categoria: CategoriaRecurso
    id_unidade_medida: UUID
    modo_controle: ModoControleRecurso

    @field_validator("descricao")
    @classmethod
    def vazio_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class ResponsavelInput(Entrada):
    instituicao_id: UUID | None = None
    pessoa_id: UUID | None = None

    @model_validator(mode="after")
    def validar_responsavel(self) -> Self:
        if (self.instituicao_id is None) == (self.pessoa_id is None):
            raise ValueError("Informe exatamente uma instituição ou pessoa responsável")
        return self


class RecursoInput(ResponsavelInput):
    tipo_recurso_id: UUID
    nome: str = Field(min_length=2, max_length=200)
    descricao: str | None = Field(default=None, max_length=4000)
    identificacao: str | None = Field(default=None, max_length=200)
    quantidade_total: Decimal = Field(ge=0, max_digits=18, decimal_places=4)
    estado_operacional: EstadoRecurso = EstadoRecurso.OPERACIONAL
    municipio_codigo_ibge: str = Field(pattern=r"^[0-9]{7}$")
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal | None = Field(
        default=None, ge=-180, le=180, max_digits=10, decimal_places=7
    )

    @field_validator("descricao", "identificacao")
    @classmethod
    def vazio_nulo(cls, valor: str | None) -> str | None:
        return valor or None

    @model_validator(mode="after")
    def validar_coordenadas(self) -> Self:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude e longitude devem ser informadas juntas")
        return self


class OfertaAtividadeInput(ResponsavelInput):
    atividade_id: UUID
    municipio_atendimento_codigo_ibge: str = Field(pattern=r"^[0-9]{7}$")
    descricao_complementar: str | None = Field(default=None, max_length=4000)
    capacidade_declarada: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=4
    )
    situacao_validacao: SituacaoValidacao = SituacaoValidacao.PENDENTE

    @field_validator("descricao_complementar")
    @classmethod
    def vazio_nulo(cls, valor: str | None) -> str | None:
        return valor or None


class OfertaRecursoInput(Entrada):
    recurso_id: UUID
    quantidade_prevista: Decimal = Field(gt=0, max_digits=18, decimal_places=4)


class TipoRecursoVM(TipoRecursoInput, AuditoriaVM):
    hash_conteudo_semantico: str
    unidade_nome: str = ""
    unidade_simbolo: str = ""
    unidade_inativa: bool = False


class ResponsavelVM(Entrada):
    responsavel_nome: str = ""
    responsavel_inativo: bool = False


class RecursoVM(RecursoInput, ResponsavelVM, AuditoriaVM):
    tipo_recurso_nome: str = ""
    tipo_recurso_inativo: bool = False
    modo_controle: ModoControleRecurso = ModoControleRecurso.INDIVIDUAL
    unidade_nome: str = ""
    unidade_simbolo: str = ""
    unidade_inativa: bool = False


class OfertaAtividadeVM(OfertaAtividadeInput, ResponsavelVM, AuditoriaVM):
    atividade_nome: str = ""
    atividade_inativa: bool = False
    unidade_nome: str | None = None
    unidade_inativa: bool = False
    validado_em: datetime | None


class OfertaRecursoVM(OfertaRecursoInput, AuditoriaVM):
    oferta_atividade_id: UUID
    recurso_nome: str = ""
    recurso_inativo: bool = False
    recurso_estado: EstadoRecurso = EstadoRecurso.OPERACIONAL
    recurso_responsavel_nome: str = ""
    unidade_simbolo: str = ""

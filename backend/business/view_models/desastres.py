from datetime import UTC, datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, StrictBool, field_validator, model_validator

from business.view_models.cadastros import AuditoriaVM
from business.view_models.capacidades import CatalogoCodigoInput
from business.view_models.qualificacoes import Entrada
from core.entity.desastres import GravidadeArea, SituacaoArea, SituacaoDesastre
from core.geometria import GeometriaArea


class GeometriaInput(Entrada):
    type: Literal["Polygon"]
    coordinates: list[list[tuple[float, float]]] = Field(min_length=1, max_length=1)

    def para_entidade(self) -> GeometriaArea:
        return GeometriaArea(coordinates=tuple(tuple(anel) for anel in self.coordinates))

    @model_validator(mode="after")
    def validar_poligono(self) -> Self:
        entidade: GeometriaArea = self.para_entidade()
        self.coordinates = [list(anel) for anel in entidade.coordinates]
        return self


class TipoDesastreInput(CatalogoCodigoInput):
    descricao: str = Field(min_length=2, max_length=4000)


class TipoDesastreVM(TipoDesastreInput, AuditoriaVM):
    pass


class ClassificacaoInput(Entrada):
    id_tipo_desastre: UUID
    principal: StrictBool


class DesastreInput(Entrada):
    titulo: str = Field(min_length=2, max_length=200)
    descricao: str = Field(min_length=2, max_length=4000)
    inicio_em: AwareDatetime
    encerramento_em: AwareDatetime | None = None
    situacao: SituacaoDesastre = SituacaoDesastre.EM_MONITORAMENTO
    id_instituicao_coordenadora: UUID
    classificacoes: list[ClassificacaoInput] = Field(min_length=1, max_length=20)

    @field_validator("inicio_em", "encerramento_em")
    @classmethod
    def normalizar_data(cls, valor: datetime | None) -> datetime | None:
        return valor.astimezone(UTC) if valor is not None else None

    @model_validator(mode="after")
    def validar_ocorrencia(self) -> Self:
        if (self.situacao == SituacaoDesastre.ENCERRADO) != (self.encerramento_em is not None):
            raise ValueError("Data de encerramento é obrigatória somente para ocorrência encerrada")
        if self.encerramento_em is not None and self.encerramento_em < self.inicio_em:
            raise ValueError("Encerramento não pode anteceder o início")
        ids: list[UUID] = [c.id_tipo_desastre for c in self.classificacoes]
        if len(set(ids)) != len(ids) or sum(c.principal for c in self.classificacoes) != 1:
            raise ValueError("Informe tipos distintos e exatamente uma classificação principal")
        return self


class DesastreTipoVM(ClassificacaoInput, AuditoriaVM):
    id_desastre: UUID
    tipo_nome: str = ""
    tipo_inativo: bool = False


class DesastreVM(AuditoriaVM, Entrada):
    titulo: str
    descricao: str
    inicio_em: datetime
    encerramento_em: datetime | None
    situacao: SituacaoDesastre
    id_instituicao_coordenadora: UUID
    coordenadora_nome: str = ""
    coordenadora_inativa: bool = False
    classificacoes: list[DesastreTipoVM] = Field(default_factory=list)


class AvaliacaoAreaInput(Entrada):
    gravidade: GravidadeArea
    situacao: SituacaoArea


class AreaAfetadaInput(AvaliacaoAreaInput):
    nome: str = Field(min_length=2, max_length=200)
    descricao: str = Field(min_length=2, max_length=4000)
    municipio_codigo_ibge: str = Field(pattern=r"^[0-9]{7}$")
    geometria: GeometriaInput


class AreaAfetadaVM(AreaAfetadaInput, AuditoriaVM):
    id_desastre: UUID
    ultima_avaliacao_em: datetime

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from core.entity.cadastros import Entidade
from core.entity.capacidades import CatalogoComCodigo
from core.geometria import GeometriaArea


class SituacaoDesastre(StrEnum):
    EM_MONITORAMENTO = "em_monitoramento"
    EM_RESPOSTA = "em_resposta"
    EM_RECUPERACAO = "em_recuperacao"
    ENCERRADO = "encerrado"


class GravidadeArea(StrEnum):
    BAIXA = "baixa"
    MODERADA = "moderada"
    ALTA = "alta"
    CRITICA = "critica"


class SituacaoArea(StrEnum):
    EM_AVALIACAO = "em_avaliacao"
    EM_RESPOSTA = "em_resposta"
    EM_RECUPERACAO = "em_recuperacao"
    ENCERRADA = "encerrada"


@dataclass(kw_only=True)
class TipoDesastre(CatalogoComCodigo):
    descricao: str


@dataclass(kw_only=True)
class Desastre(Entidade):
    titulo: str
    descricao: str
    inicio_em: datetime
    situacao: SituacaoDesastre
    id_instituicao_coordenadora: UUID
    encerramento_em: datetime | None = None


@dataclass(kw_only=True)
class DesastreTipo(Entidade):
    id_desastre: UUID
    id_tipo_desastre: UUID
    principal: bool


@dataclass(kw_only=True)
class AreaAfetada(Entidade):
    id_desastre: UUID
    nome: str
    descricao: str
    municipio_codigo_ibge: str
    geometria: GeometriaArea
    gravidade: GravidadeArea
    situacao: SituacaoArea
    ultima_avaliacao_em: datetime

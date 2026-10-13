from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Severidade(StrEnum):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Mensagem(BaseModel):
    severity: Severidade
    code: str
    text: str


def sem_mensagens(valor: list[Mensagem] | None) -> bool:
    return not valor


class ApiResponse[T](BaseModel):
    data: T
    messages: list[Mensagem] | None = Field(default=None, exclude_if=sem_mensagens)


class Problema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str


class ErroNegocio(Exception):
    def __init__(self, status: int, titulo: str, detalhe: str) -> None:
        self.status: int = status
        self.titulo: str = titulo
        self.detalhe: str = detalhe
        super().__init__(detalhe)

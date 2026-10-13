import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException

from core.http.contratos import ErroNegocio, Problema

logger: logging.Logger = logging.getLogger("redesolidaria")


async def tratar_erro(request: Request, erro: Exception) -> JSONResponse:
    status: int
    titulo: str
    detalhe: str
    if isinstance(erro, ErroNegocio):
        status, titulo, detalhe = erro.status, erro.titulo, erro.detalhe
    elif isinstance(erro, RequestValidationError):
        status, titulo = 422, "Dados inválidos"
        detalhe = "Verifique os campos e tipos exigidos no contrato da operação."
    elif isinstance(erro, IntegrityError):
        status, titulo, detalhe = (
            409,
            "Conflito de cadastro",
            "Os dados conflitam com uma restrição do banco.",
        )
    elif isinstance(erro, OperationalError):
        status, titulo, detalhe = (
            503,
            "Banco indisponível",
            "Não foi possível acessar o banco de dados.",
        )
    elif isinstance(erro, HTTPException):
        status, titulo, detalhe = (
            erro.status_code,
            "Falha na requisição",
            "A operação não pôde ser atendida.",
        )
    else:
        status, titulo, detalhe = 500, "Erro interno", "Não foi possível concluir a operação."
        # Não registrar corpo, token, URL de conexão ou mensagem bruta de integrações.
        logger.error("erro_interno classe=%s", type(erro).__name__)
    problema: Problema = Problema(
        title=titulo, status=status, detail=detalhe, instance=request.url.path
    )
    return JSONResponse(
        status_code=status,
        content=problema.model_dump(mode="json"),
        media_type="application/problem+json",
        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
    )

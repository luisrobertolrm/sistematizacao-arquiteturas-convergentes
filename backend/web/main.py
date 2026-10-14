import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from business.view_models.cadastros import StatusVM
from core.http.contratos import ApiResponse, ErroNegocio
from core.ia_operacao import FabricaClientesIA
from infra.ia.clientes import FabricaLangChain
from web.controllers.cadastros import criar_router
from web.controllers.capacidades import criar_router_capacidades
from web.controllers.desastres import criar_router_desastres
from web.controllers.operacao import criar_router_operacao
from web.controllers.qualificacoes import criar_router_qualificacoes
from web.controllers.recursos import criar_router_recursos
from web.middlewares.erros import tratar_erro
from web.settings import Settings

logger: logging.Logger = logging.getLogger("redesolidaria")

# SPA Angular buildada e copiada no Docker (stage web -> static/app). Em dev a pasta nao
# existe, entao nada e montado e o front continua no dev server (ng serve, porta 4200).
_SPA_DIR = Path(__file__).resolve().parent / "static" / "app"


class _SpaStaticFiles(StaticFiles):
    """Estaticos do Angular com fallback para index.html (deep-links / reload de rota do SPA)."""

    async def get_response(self, path: str, scope: Any) -> Response:
        response: Response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response("index.html", scope)
        return response


def create_app(
    settings: Settings | None = None,
    engine: Engine | None = None,
    clientes_ia: FabricaClientesIA | None = None,
) -> FastAPI:
    configuracao: Settings = settings or Settings()
    banco: Engine = engine or create_engine(
        configuracao.database_url.get_secret_value(),
        pool_pre_ping=True,
        hide_parameters=True,
    )
    fabrica: sessionmaker[Session] = sessionmaker(banco, expire_on_commit=False)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        banco.dispose()

    aplicacao: FastAPI = FastAPI(title="RedeSolidária API", version="0.1.0", lifespan=lifespan)
    aplicacao.add_middleware(
        CORSMiddleware,
        allow_origins=configuracao.cors_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )
    for erro in (
        ErroNegocio,
        RequestValidationError,
        IntegrityError,
        OperationalError,
        HTTPException,
        Exception,
    ):
        aplicacao.add_exception_handler(erro, tratar_erro)

    @aplicacao.middleware("http")
    async def registrar_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
        inicio: float = perf_counter()
        response: Response = await call_next(request)
        logger.info(
            "http metodo=%s status=%d duracao_ms=%.1f",
            request.method,
            response.status_code,
            (perf_counter() - inicio) * 1000,
        )
        return response

    @aplicacao.get("/health", tags=["Saúde"])
    def health() -> ApiResponse[StatusVM]:
        return ApiResponse(data=StatusVM(status="ok"))

    aplicacao.include_router(criar_router(fabrica, configuracao))
    aplicacao.include_router(criar_router_qualificacoes(fabrica, configuracao))
    aplicacao.include_router(criar_router_capacidades(fabrica, configuracao))
    aplicacao.include_router(criar_router_recursos(fabrica, configuracao))
    aplicacao.include_router(criar_router_desastres(fabrica, configuracao))
    aplicacao.include_router(
        criar_router_operacao(fabrica, configuracao, clientes_ia or FabricaLangChain())
    )
    # SPA por ultimo: os routers de API (/api/v1, /health, /docs) tem precedencia;
    # o mount em "/" so captura o que sobra, servindo o front na mesma origem (sem CORS).
    if (_SPA_DIR / "index.html").exists():
        aplicacao.mount("/", _SpaStaticFiles(directory=str(_SPA_DIR), html=True), name="spa")
    return aplicacao


app: FastAPI = create_app()

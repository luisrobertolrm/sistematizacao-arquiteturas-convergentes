from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, sessionmaker

from business.servico.recursos import (
    OfertaAtividadeService,
    OfertaRecursoService,
    RecursoService,
    TipoRecursoService,
)
from business.view_models.recursos import (
    OfertaAtividadeInput,
    OfertaAtividadeVM,
    OfertaRecursoInput,
    OfertaRecursoVM,
    RecursoInput,
    RecursoVM,
    TipoRecursoInput,
    TipoRecursoVM,
)
from core.http.contratos import ApiResponse
from web.autenticacao.jwt import Principal, autenticacao
from web.settings import Settings


def criar_router_recursos(fabrica: sessionmaker[Session], settings: Settings) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/api/v1", tags=["Recursos e ofertas"])
    exigir_admin = autenticacao(settings)

    def sessao() -> Iterator[Session]:
        with fabrica() as unidade:
            yield unidade

    def tipos_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> TipoRecursoService:
        return TipoRecursoService(unidade)

    @router.get("/tipos-recurso")
    def listar_tipos(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoRecursoService, Depends(tipos_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[TipoRecursoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/tipos-recurso/{identificador}")
    def obter_tipos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoRecursoService, Depends(tipos_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[TipoRecursoVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/tipos-recurso", status_code=201)
    def criar_tipos(
        dados: TipoRecursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoRecursoService, Depends(tipos_service)],
    ) -> ApiResponse[TipoRecursoVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/tipos-recurso/{identificador}")
    def editar_tipos(
        identificador: UUID,
        dados: TipoRecursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoRecursoService, Depends(tipos_service)],
    ) -> ApiResponse[TipoRecursoVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/tipos-recurso/{identificador}")
    def inativar_tipos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoRecursoService, Depends(tipos_service)],
    ) -> ApiResponse[TipoRecursoVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def recursos_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> RecursoService:
        return RecursoService(unidade)

    @router.get("/recursos")
    def listar_recursos(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecursoService, Depends(recursos_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[RecursoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/recursos/{identificador}")
    def obter_recursos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecursoService, Depends(recursos_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[RecursoVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/recursos", status_code=201)
    def criar_recursos(
        dados: RecursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecursoService, Depends(recursos_service)],
    ) -> ApiResponse[RecursoVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/recursos/{identificador}")
    def editar_recursos(
        identificador: UUID,
        dados: RecursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecursoService, Depends(recursos_service)],
    ) -> ApiResponse[RecursoVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/recursos/{identificador}")
    def inativar_recursos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecursoService, Depends(recursos_service)],
    ) -> ApiResponse[RecursoVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def ofertas_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> OfertaAtividadeService:
        return OfertaAtividadeService(unidade)

    @router.get("/ofertas-atividade")
    def listar_ofertas(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaAtividadeService, Depends(ofertas_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[OfertaAtividadeVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/ofertas-atividade/{identificador}")
    def obter_ofertas(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaAtividadeService, Depends(ofertas_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[OfertaAtividadeVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/ofertas-atividade", status_code=201)
    def criar_ofertas(
        dados: OfertaAtividadeInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaAtividadeService, Depends(ofertas_service)],
    ) -> ApiResponse[OfertaAtividadeVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/ofertas-atividade/{identificador}")
    def editar_ofertas(
        identificador: UUID,
        dados: OfertaAtividadeInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaAtividadeService, Depends(ofertas_service)],
    ) -> ApiResponse[OfertaAtividadeVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/ofertas-atividade/{identificador}")
    def inativar_ofertas(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaAtividadeService, Depends(ofertas_service)],
    ) -> ApiResponse[OfertaAtividadeVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def vinculos_service(
        oferta_id: UUID,
        unidade: Annotated[Session, Depends(sessao)],
    ) -> OfertaRecursoService:
        return OfertaRecursoService(unidade, oferta_id)

    @router.get("/ofertas-atividade/{oferta_id}/recursos")
    def listar_vinculos(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaRecursoService, Depends(vinculos_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[OfertaRecursoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/ofertas-atividade/{oferta_id}/recursos/{identificador}")
    def obter_vinculos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaRecursoService, Depends(vinculos_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[OfertaRecursoVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/ofertas-atividade/{oferta_id}/recursos", status_code=201)
    def criar_vinculos(
        dados: OfertaRecursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaRecursoService, Depends(vinculos_service)],
    ) -> ApiResponse[OfertaRecursoVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/ofertas-atividade/{oferta_id}/recursos/{identificador}")
    def editar_vinculos(
        identificador: UUID,
        dados: OfertaRecursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaRecursoService, Depends(vinculos_service)],
    ) -> ApiResponse[OfertaRecursoVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/ofertas-atividade/{oferta_id}/recursos/{identificador}")
    def inativar_vinculos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[OfertaRecursoService, Depends(vinculos_service)],
    ) -> ApiResponse[OfertaRecursoVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    return router

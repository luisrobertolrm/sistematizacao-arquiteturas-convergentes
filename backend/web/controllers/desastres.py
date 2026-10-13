from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, sessionmaker

from business.servico.desastres import AreaAfetadaService, DesastreService, TipoDesastreService
from business.view_models.desastres import (
    AreaAfetadaInput,
    AreaAfetadaVM,
    AvaliacaoAreaInput,
    DesastreInput,
    DesastreVM,
    TipoDesastreInput,
    TipoDesastreVM,
)
from core.http.contratos import ApiResponse
from web.autenticacao.jwt import Principal, autenticacao
from web.settings import Settings


def criar_router_desastres(fabrica: sessionmaker[Session], settings: Settings) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/api/v1", tags=["Desastres e áreas"])
    exigir_admin = autenticacao(settings)

    def sessao() -> Iterator[Session]:
        with fabrica() as unidade:
            yield unidade

    def tipos_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> TipoDesastreService:
        return TipoDesastreService(unidade)

    @router.get("/tipos-desastre")
    def listar_tipos(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoDesastreService, Depends(tipos_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[TipoDesastreVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/tipos-desastre/{identificador}")
    def obter_tipos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoDesastreService, Depends(tipos_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[TipoDesastreVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/tipos-desastre", status_code=201)
    def criar_tipos(
        dados: TipoDesastreInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoDesastreService, Depends(tipos_service)],
    ) -> ApiResponse[TipoDesastreVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/tipos-desastre/{identificador}")
    def editar_tipos(
        identificador: UUID,
        dados: TipoDesastreInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoDesastreService, Depends(tipos_service)],
    ) -> ApiResponse[TipoDesastreVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/tipos-desastre/{identificador}")
    def inativar_tipos(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[TipoDesastreService, Depends(tipos_service)],
    ) -> ApiResponse[TipoDesastreVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def desastres_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> DesastreService:
        return DesastreService(unidade)

    @router.get("/desastres")
    def listar_desastres(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DesastreService, Depends(desastres_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[DesastreVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/desastres/{identificador}")
    def obter_desastres(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DesastreService, Depends(desastres_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[DesastreVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/desastres", status_code=201)
    def criar_desastres(
        dados: DesastreInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DesastreService, Depends(desastres_service)],
    ) -> ApiResponse[DesastreVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/desastres/{identificador}")
    def editar_desastres(
        identificador: UUID,
        dados: DesastreInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DesastreService, Depends(desastres_service)],
    ) -> ApiResponse[DesastreVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/desastres/{identificador}")
    def inativar_desastres(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DesastreService, Depends(desastres_service)],
    ) -> ApiResponse[DesastreVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def areas_service(
        id_desastre: UUID,
        unidade: Annotated[Session, Depends(sessao)],
    ) -> AreaAfetadaService:
        return AreaAfetadaService(unidade, id_desastre)

    @router.get("/desastres/{id_desastre}/areas")
    def listar_areas(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AreaAfetadaService, Depends(areas_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[AreaAfetadaVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/desastres/{id_desastre}/areas/{identificador}")
    def obter_areas(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AreaAfetadaService, Depends(areas_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[AreaAfetadaVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/desastres/{id_desastre}/areas", status_code=201)
    def criar_areas(
        dados: AreaAfetadaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AreaAfetadaService, Depends(areas_service)],
    ) -> ApiResponse[AreaAfetadaVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/desastres/{id_desastre}/areas/{identificador}")
    def editar_areas(
        identificador: UUID,
        dados: AreaAfetadaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AreaAfetadaService, Depends(areas_service)],
    ) -> ApiResponse[AreaAfetadaVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/desastres/{id_desastre}/areas/{identificador}")
    def inativar_areas(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AreaAfetadaService, Depends(areas_service)],
    ) -> ApiResponse[AreaAfetadaVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    @router.post("/desastres/{id_desastre}/areas/{identificador}/avaliar")
    def avaliar_area(
        identificador: UUID,
        dados: AvaliacaoAreaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AreaAfetadaService, Depends(areas_service)],
    ) -> ApiResponse[AreaAfetadaVM]:
        return ApiResponse(data=service.avaliar(identificador, dados, admin.sub))

    return router

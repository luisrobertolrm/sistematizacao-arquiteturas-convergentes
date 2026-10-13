from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, sessionmaker

from business.servico.capacidades import (
    AtividadeService,
    AtividadeTermoService,
    CategoriaAtividadeService,
    UnidadeMedidaService,
)
from business.view_models.capacidades import (
    AtividadeInput,
    AtividadeTermoInput,
    AtividadeTermoVM,
    AtividadeVM,
    CategoriaAtividadeInput,
    CategoriaAtividadeVM,
    UnidadeMedidaInput,
    UnidadeMedidaVM,
)
from core.http.contratos import ApiResponse
from web.autenticacao.jwt import Principal, autenticacao
from web.settings import Settings


def criar_router_capacidades(fabrica: sessionmaker[Session], settings: Settings) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/api/v1")
    exigir_admin = autenticacao(settings)

    def sessao() -> Iterator[Session]:
        with fabrica() as unidade:
            yield unidade

    def unidades_medida_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> UnidadeMedidaService:
        return UnidadeMedidaService(unidade)

    @router.get("/unidades-medida", tags=["Capacidades"])
    def listar_unidades_medida(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[UnidadeMedidaService, Depends(unidades_medida_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[UnidadeMedidaVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/unidades-medida/{identificador}", tags=["Capacidades"])
    def obter_unidades_medida(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[UnidadeMedidaService, Depends(unidades_medida_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[UnidadeMedidaVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/unidades-medida", status_code=201, tags=["Capacidades"])
    def criar_unidades_medida(
        dados: UnidadeMedidaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[UnidadeMedidaService, Depends(unidades_medida_service)],
    ) -> ApiResponse[UnidadeMedidaVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/unidades-medida/{identificador}", tags=["Capacidades"])
    def editar_unidades_medida(
        identificador: UUID,
        dados: UnidadeMedidaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[UnidadeMedidaService, Depends(unidades_medida_service)],
    ) -> ApiResponse[UnidadeMedidaVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/unidades-medida/{identificador}", tags=["Capacidades"])
    def inativar_unidades_medida(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[UnidadeMedidaService, Depends(unidades_medida_service)],
    ) -> ApiResponse[UnidadeMedidaVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def categorias_atividade_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> CategoriaAtividadeService:
        return CategoriaAtividadeService(unidade)

    @router.get("/categorias-atividade", tags=["Capacidades"])
    def listar_categorias_atividade(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CategoriaAtividadeService, Depends(categorias_atividade_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[CategoriaAtividadeVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/categorias-atividade/{identificador}", tags=["Capacidades"])
    def obter_categorias_atividade(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CategoriaAtividadeService, Depends(categorias_atividade_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[CategoriaAtividadeVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/categorias-atividade", status_code=201, tags=["Capacidades"])
    def criar_categorias_atividade(
        dados: CategoriaAtividadeInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CategoriaAtividadeService, Depends(categorias_atividade_service)],
    ) -> ApiResponse[CategoriaAtividadeVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/categorias-atividade/{identificador}", tags=["Capacidades"])
    def editar_categorias_atividade(
        identificador: UUID,
        dados: CategoriaAtividadeInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CategoriaAtividadeService, Depends(categorias_atividade_service)],
    ) -> ApiResponse[CategoriaAtividadeVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/categorias-atividade/{identificador}", tags=["Capacidades"])
    def inativar_categorias_atividade(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CategoriaAtividadeService, Depends(categorias_atividade_service)],
    ) -> ApiResponse[CategoriaAtividadeVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def atividades_service(unidade: Annotated[Session, Depends(sessao)]) -> AtividadeService:
        return AtividadeService(unidade)

    @router.get("/atividades", tags=["Capacidades"])
    def listar_atividades(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeService, Depends(atividades_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[AtividadeVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca, incluir_inativos))

    @router.get("/atividades/{identificador}", tags=["Capacidades"])
    def obter_atividades(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeService, Depends(atividades_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[AtividadeVM]:
        return ApiResponse(data=service.obter(identificador, incluir_inativos))

    @router.post("/atividades", status_code=201, tags=["Capacidades"])
    def criar_atividades(
        dados: AtividadeInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeService, Depends(atividades_service)],
    ) -> ApiResponse[AtividadeVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/atividades/{identificador}", tags=["Capacidades"])
    def editar_atividades(
        identificador: UUID,
        dados: AtividadeInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeService, Depends(atividades_service)],
    ) -> ApiResponse[AtividadeVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/atividades/{identificador}", tags=["Capacidades"])
    def inativar_atividades(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeService, Depends(atividades_service)],
    ) -> ApiResponse[AtividadeVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def termos_service(unidade: Annotated[Session, Depends(sessao)]) -> AtividadeTermoService:
        return AtividadeTermoService(unidade)

    @router.get("/atividades/{atividade_id}/termos", tags=["Termos de atividades"])
    def listar_termos(
        atividade_id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeTermoService, Depends(termos_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[AtividadeTermoVM]]:
        return ApiResponse(
            data=service.listar(atividade_id, limite, deslocamento, incluir_inativos)
        )

    @router.get("/atividades/{atividade_id}/termos/{identificador}", tags=["Termos de atividades"])
    def obter_termo(
        atividade_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeTermoService, Depends(termos_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[AtividadeTermoVM]:
        return ApiResponse(data=service.obter(atividade_id, identificador, incluir_inativos))

    @router.post(
        "/atividades/{atividade_id}/termos", status_code=201, tags=["Termos de atividades"]
    )
    def criar_termo(
        atividade_id: UUID,
        dados: AtividadeTermoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeTermoService, Depends(termos_service)],
    ) -> ApiResponse[AtividadeTermoVM]:
        return ApiResponse(data=service.alterar(atividade_id, None, dados, admin.sub))

    @router.put("/atividades/{atividade_id}/termos/{identificador}", tags=["Termos de atividades"])
    def editar_termo(
        atividade_id: UUID,
        identificador: UUID,
        dados: AtividadeTermoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeTermoService, Depends(termos_service)],
    ) -> ApiResponse[AtividadeTermoVM]:
        return ApiResponse(data=service.alterar(atividade_id, identificador, dados, admin.sub))

    @router.delete(
        "/atividades/{atividade_id}/termos/{identificador}", tags=["Termos de atividades"]
    )
    def inativar_termo(
        atividade_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[AtividadeTermoService, Depends(termos_service)],
    ) -> ApiResponse[AtividadeTermoVM]:
        return ApiResponse(data=service.alterar(atividade_id, identificador, None, admin.sub))

    return router

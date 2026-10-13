from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, sessionmaker

from business.servico.demandas import DemandasService
from business.servico.indices import IndicesService
from business.servico.modelos_ia import ModelosIAService
from business.servico.recomendacoes import RecomendacoesService
from business.view_models.desastres import AreaAfetadaVM
from business.view_models.operacao import (
    BuscaInput,
    BuscaVM,
    ConexaoInput,
    ConexaoVM,
    DecisaoInput,
    DemandaInput,
    DemandaVM,
    IndexarInput,
    IndiceVM,
    ModeloInput,
    ModeloVM,
    RecomendacaoVM,
)
from core.http.contratos import ApiResponse
from core.ia_operacao import FabricaClientesIA
from web.autenticacao.jwt import Principal, autenticacao
from web.settings import Settings


def criar_router_operacao(
    fabrica: sessionmaker[Session], settings: Settings, clientes: FabricaClientesIA
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["IA, demandas e recomendações"])
    exigir_admin = autenticacao(settings)

    def sessao() -> Iterator[Session]:
        with fabrica() as s:
            yield s

    def modelos(s: Annotated[Session, Depends(sessao)]) -> ModelosIAService:
        return ModelosIAService(
            s, settings.encryption_key, settings.encryption_key_id, settings.ia_urls_permitidas
        )

    def pedidos(s: Annotated[Session, Depends(sessao)]) -> DemandasService:
        return DemandasService(s)

    def indices(
        s: Annotated[Session, Depends(sessao)], m: Annotated[ModelosIAService, Depends(modelos)]
    ) -> IndicesService:
        return IndicesService(s, m, clientes)

    def sugestoes(
        s: Annotated[Session, Depends(sessao)], m: Annotated[ModelosIAService, Depends(modelos)]
    ) -> RecomendacoesService:
        return RecomendacoesService(s, m, clientes)

    @router.get("/conexoes-ia")
    def listar_conexao(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[ConexaoVM]]:
        return ApiResponse(
            data=[
                service.conexao_vm(e)
                for e in service.conexoes.listar(limite, deslocamento, busca, incluir_inativos)
            ]
        )

    @router.get("/conexoes-ia/{id}")
    def obter_conexao(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[ConexaoVM]:
        return ApiResponse(data=service.conexao_vm(service.conexoes.exigir(id, incluir_inativos)))

    @router.post("/conexoes-ia", status_code=201)
    def criar_conexao(
        dados: ConexaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
    ) -> ApiResponse[ConexaoVM]:
        return ApiResponse(data=service.salvar_conexao(None, dados, admin.sub))

    @router.put("/conexoes-ia/{id}")
    def editar_conexao(
        id: UUID,
        dados: ConexaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
    ) -> ApiResponse[ConexaoVM]:
        return ApiResponse(data=service.salvar_conexao(id, dados, admin.sub))

    @router.delete("/conexoes-ia/{id}")
    def inativar_conexao(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
    ) -> ApiResponse[ConexaoVM]:
        return ApiResponse(data=service.inativar_conexao(id, admin.sub))

    @router.get("/modelos-ia")
    def listar_modelo(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[ModeloVM]]:
        return ApiResponse(
            data=[
                service.modelo_vm(e)
                for e in service.modelos.listar(limite, deslocamento, busca, incluir_inativos)
            ]
        )

    @router.get("/modelos-ia/{id}")
    def obter_modelo(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[ModeloVM]:
        return ApiResponse(data=service.modelo_vm(service.modelos.exigir(id, incluir_inativos)))

    @router.post("/modelos-ia", status_code=201)
    def criar_modelo(
        dados: ModeloInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
    ) -> ApiResponse[ModeloVM]:
        return ApiResponse(data=service.salvar_modelo(None, dados, admin.sub))

    @router.put("/modelos-ia/{id}")
    def editar_modelo(
        id: UUID,
        dados: ModeloInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
    ) -> ApiResponse[ModeloVM]:
        return ApiResponse(data=service.salvar_modelo(id, dados, admin.sub))

    @router.delete("/modelos-ia/{id}")
    def inativar_modelo(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ModelosIAService, Depends(modelos)],
    ) -> ApiResponse[ModeloVM]:
        return ApiResponse(data=service.inativar_modelo(id, admin.sub))

    @router.get("/demandas")
    def listar_demandas(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DemandasService, Depends(pedidos)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
        id_area_afetada: UUID | None = None,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[DemandaVM]]:
        return ApiResponse(
            data=service.listar(limite, deslocamento, busca, incluir_inativos, id_area_afetada)
        )

    @router.get("/demandas/{id}")
    def obter_demanda(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DemandasService, Depends(pedidos)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[DemandaVM]:
        return ApiResponse(
            data=service.visualizar(service.repo.exigir(id, incluir_inativos), incluir_inativos)
        )

    @router.post("/demandas", status_code=201)
    def criar_demanda(
        dados: DemandaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DemandasService, Depends(pedidos)],
    ) -> ApiResponse[DemandaVM]:
        return ApiResponse(data=service.salvar(None, dados, admin.sub))

    @router.put("/demandas/{id}")
    def editar_demanda(
        id: UUID,
        dados: DemandaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DemandasService, Depends(pedidos)],
    ) -> ApiResponse[DemandaVM]:
        return ApiResponse(data=service.salvar(id, dados, admin.sub))

    @router.delete("/demandas/{id}")
    def inativar_demanda(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DemandasService, Depends(pedidos)],
    ) -> ApiResponse[DemandaVM]:
        return ApiResponse(data=service.inativar(id, admin.sub))

    @router.get("/indices-atividade")
    def listar_indices(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[IndicesService, Depends(indices)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        id_modelo: UUID | None = None,
    ) -> ApiResponse[list[IndiceVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, id_modelo))

    @router.post("/indices-atividade/indexar")
    def indexar(
        dados: IndexarInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[IndicesService, Depends(indices)],
    ) -> ApiResponse[list[IndiceVM]]:
        return ApiResponse(data=service.indexar(dados, admin.sub))

    @router.post("/atividades/busca-semantica")
    def buscar(
        dados: BuscaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[IndicesService, Depends(indices)],
    ) -> ApiResponse[BuscaVM]:
        return ApiResponse(data=service.buscar(dados))

    @router.post("/demandas/{id}/recomendacoes", status_code=201)
    def gerar(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecomendacoesService, Depends(sugestoes)],
    ) -> ApiResponse[RecomendacaoVM]:
        return ApiResponse(data=service.gerar(id, admin.sub))

    @router.get("/recomendacoes")
    def listar_recomendacoes(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecomendacoesService, Depends(sugestoes)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        id_demanda: UUID | None = None,
    ) -> ApiResponse[list[RecomendacaoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, id_demanda))

    @router.get("/recomendacoes/{id}")
    def obter_recomendacao(
        id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecomendacoesService, Depends(sugestoes)],
    ) -> ApiResponse[RecomendacaoVM]:
        return ApiResponse(data=service.visualizar(service.repo.exigir(id)))

    @router.post("/recomendacoes/{id}/decisao")
    def decidir(
        id: UUID,
        dados: DecisaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[RecomendacoesService, Depends(sugestoes)],
    ) -> ApiResponse[RecomendacaoVM]:
        return ApiResponse(data=service.decidir(id, dados, admin.sub))

    @router.get("/areas-afetadas")
    def listar_areas_referencia(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[DemandasService, Depends(pedidos)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    ) -> ApiResponse[list[AreaAfetadaVM]]:
        return ApiResponse(data=service.listar_areas_referencia(limite, deslocamento, busca))

    return router

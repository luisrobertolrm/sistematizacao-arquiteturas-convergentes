from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, sessionmaker

from business.servico.cadastros import InstituicaoService, PessoaService
from business.view_models.cadastros import (
    CadastroPublicoPessoaInput,
    InstituicaoInput,
    InstituicaoVM,
    PessoaInput,
    PessoaVM,
    TokenAdminVM,
    VerificacaoEmailInput,
)
from core.http.contratos import ApiResponse
from web.autenticacao.emitir_token import gerar_token_admin
from web.autenticacao.jwt import Principal, autenticacao
from web.settings import Settings


def criar_router(fabrica: sessionmaker[Session], settings: Settings) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/api/v1")
    exigir_admin = autenticacao(settings)

    def sessao() -> Iterator[Session]:
        with fabrica() as unidade:
            yield unidade

    def instituicao_service(unidade: Annotated[Session, Depends(sessao)]) -> InstituicaoService:
        return InstituicaoService(unidade)

    def pessoa_service(unidade: Annotated[Session, Depends(sessao)]) -> PessoaService:
        return PessoaService(unidade)

    @router.post("/autenticacao/token-admin", tags=["Autenticação"])
    def emitir_token_admin() -> ApiResponse[TokenAdminVM]:
        token: str = gerar_token_admin(settings)
        return ApiResponse(data=TokenAdminVM(token=token, expira_em_minutos=60))

    @router.post("/publico/pessoas", status_code=201, tags=["Cadastro Público"])
    def autocadastrar_pessoa(
        dados: CadastroPublicoPessoaInput,
        service: Annotated[PessoaService, Depends(pessoa_service)],
    ) -> ApiResponse[PessoaVM]:
        return ApiResponse(data=service.autocadastrar(dados))

    @router.post("/publico/pessoas/verificar-email", tags=["Cadastro Público"])
    def verificar_email_pessoa(
        dados: VerificacaoEmailInput,
        service: Annotated[PessoaService, Depends(pessoa_service)],
    ) -> ApiResponse[PessoaVM]:
        return ApiResponse(data=service.verificar_por_email(dados))

    @router.get("/instituicoes", tags=["Instituições"])
    def listar_instituicoes(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[InstituicaoService, Depends(instituicao_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    ) -> ApiResponse[list[InstituicaoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca))

    @router.get("/instituicoes/{identificador}", tags=["Instituições"])
    def obter_instituicao(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[InstituicaoService, Depends(instituicao_service)],
    ) -> ApiResponse[InstituicaoVM]:
        return ApiResponse(data=service.obter(identificador))

    @router.post("/instituicoes", status_code=201, tags=["Instituições"])
    def criar_instituicao(
        dados: InstituicaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[InstituicaoService, Depends(instituicao_service)],
    ) -> ApiResponse[InstituicaoVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/instituicoes/{identificador}", tags=["Instituições"])
    def editar_instituicao(
        identificador: UUID,
        dados: InstituicaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[InstituicaoService, Depends(instituicao_service)],
    ) -> ApiResponse[InstituicaoVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/instituicoes/{identificador}", tags=["Instituições"])
    def inativar_instituicao(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[InstituicaoService, Depends(instituicao_service)],
    ) -> ApiResponse[InstituicaoVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    @router.get("/pessoas", tags=["Pessoas"])
    def listar_pessoas(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaService, Depends(pessoa_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    ) -> ApiResponse[list[PessoaVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca))

    @router.get("/pessoas/{identificador}", tags=["Pessoas"])
    def obter_pessoa(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaService, Depends(pessoa_service)],
    ) -> ApiResponse[PessoaVM]:
        return ApiResponse(data=service.obter(identificador))

    @router.post("/pessoas", status_code=201, tags=["Pessoas"])
    def criar_pessoa(
        dados: PessoaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaService, Depends(pessoa_service)],
    ) -> ApiResponse[PessoaVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/pessoas/{identificador}", tags=["Pessoas"])
    def editar_pessoa(
        identificador: UUID,
        dados: PessoaInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaService, Depends(pessoa_service)],
    ) -> ApiResponse[PessoaVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/pessoas/{identificador}", tags=["Pessoas"])
    def inativar_pessoa(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaService, Depends(pessoa_service)],
    ) -> ApiResponse[PessoaVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    return router


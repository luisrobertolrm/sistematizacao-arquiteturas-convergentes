from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, sessionmaker

from business.servico.qualificacoes import (
    CursoService,
    PessoaCursoService,
    PessoaInstituicaoService,
    PessoaProfissaoService,
    ProfissaoService,
)
from business.view_models.qualificacoes import (
    CursoInput,
    CursoVM,
    PessoaCursoInput,
    PessoaCursoVM,
    PessoaInstituicaoInput,
    PessoaInstituicaoVM,
    PessoaProfissaoInput,
    PessoaProfissaoVM,
    ProfissaoInput,
    ProfissaoVM,
)
from core.http.contratos import ApiResponse
from web.autenticacao.jwt import Principal, autenticacao
from web.settings import Settings


def criar_router_qualificacoes(fabrica: sessionmaker[Session], settings: Settings) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/api/v1")
    exigir_admin = autenticacao(settings)

    def sessao() -> Iterator[Session]:
        with fabrica() as unidade:
            yield unidade

    def profissao_service(unidade: Annotated[Session, Depends(sessao)]) -> ProfissaoService:
        return ProfissaoService(unidade)

    @router.get("/profissoes", tags=["Catálogos"])
    def listar_profissao(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ProfissaoService, Depends(profissao_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    ) -> ApiResponse[list[ProfissaoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca))

    @router.get("/profissoes/{identificador}", tags=["Catálogos"])
    def obter_profissao(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ProfissaoService, Depends(profissao_service)],
    ) -> ApiResponse[ProfissaoVM]:
        return ApiResponse(data=service.obter(identificador))

    @router.post("/profissoes", status_code=201, tags=["Catálogos"])
    def criar_profissao(
        dados: ProfissaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ProfissaoService, Depends(profissao_service)],
    ) -> ApiResponse[ProfissaoVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/profissoes/{identificador}", tags=["Catálogos"])
    def editar_profissao(
        identificador: UUID,
        dados: ProfissaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ProfissaoService, Depends(profissao_service)],
    ) -> ApiResponse[ProfissaoVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/profissoes/{identificador}", tags=["Catálogos"])
    def inativar_profissao(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[ProfissaoService, Depends(profissao_service)],
    ) -> ApiResponse[ProfissaoVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def curso_service(unidade: Annotated[Session, Depends(sessao)]) -> CursoService:
        return CursoService(unidade)

    @router.get("/cursos", tags=["Catálogos"])
    def listar_curso(
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CursoService, Depends(curso_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        busca: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    ) -> ApiResponse[list[CursoVM]]:
        return ApiResponse(data=service.listar(limite, deslocamento, busca))

    @router.get("/cursos/{identificador}", tags=["Catálogos"])
    def obter_curso(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CursoService, Depends(curso_service)],
    ) -> ApiResponse[CursoVM]:
        return ApiResponse(data=service.obter(identificador))

    @router.post("/cursos", status_code=201, tags=["Catálogos"])
    def criar_curso(
        dados: CursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CursoService, Depends(curso_service)],
    ) -> ApiResponse[CursoVM]:
        return ApiResponse(data=service.criar(dados, admin.sub))

    @router.put("/cursos/{identificador}", tags=["Catálogos"])
    def editar_curso(
        identificador: UUID,
        dados: CursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CursoService, Depends(curso_service)],
    ) -> ApiResponse[CursoVM]:
        return ApiResponse(data=service.editar(identificador, dados, admin.sub))

    @router.delete("/cursos/{identificador}", tags=["Catálogos"])
    def inativar_curso(
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[CursoService, Depends(curso_service)],
    ) -> ApiResponse[CursoVM]:
        return ApiResponse(data=service.inativar(identificador, admin.sub))

    def pessoa_instituicao_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> PessoaInstituicaoService:
        return PessoaInstituicaoService(unidade)

    @router.get("/pessoas/{pessoa_id}/instituicoes", tags=["Vínculos e qualificações"])
    def listar_pessoa_instituicao(
        pessoa_id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaInstituicaoService, Depends(pessoa_instituicao_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[PessoaInstituicaoVM]]:
        return ApiResponse(data=service.listar(pessoa_id, limite, deslocamento, incluir_inativos))

    @router.get(
        "/pessoas/{pessoa_id}/instituicoes/{identificador}", tags=["Vínculos e qualificações"]
    )
    def obter_pessoa_instituicao(
        pessoa_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaInstituicaoService, Depends(pessoa_instituicao_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[PessoaInstituicaoVM]:
        return ApiResponse(data=service.obter(pessoa_id, identificador, incluir_inativos))

    @router.post(
        "/pessoas/{pessoa_id}/instituicoes", status_code=201, tags=["Vínculos e qualificações"]
    )
    def criar_pessoa_instituicao(
        pessoa_id: UUID,
        dados: PessoaInstituicaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaInstituicaoService, Depends(pessoa_instituicao_service)],
    ) -> ApiResponse[PessoaInstituicaoVM]:
        return ApiResponse(data=service.criar(pessoa_id, dados, admin.sub))

    @router.put(
        "/pessoas/{pessoa_id}/instituicoes/{identificador}", tags=["Vínculos e qualificações"]
    )
    def editar_pessoa_instituicao(
        pessoa_id: UUID,
        identificador: UUID,
        dados: PessoaInstituicaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaInstituicaoService, Depends(pessoa_instituicao_service)],
    ) -> ApiResponse[PessoaInstituicaoVM]:
        return ApiResponse(data=service.editar(pessoa_id, identificador, dados, admin.sub))

    @router.delete(
        "/pessoas/{pessoa_id}/instituicoes/{identificador}", tags=["Vínculos e qualificações"]
    )
    def inativar_pessoa_instituicao(
        pessoa_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaInstituicaoService, Depends(pessoa_instituicao_service)],
    ) -> ApiResponse[PessoaInstituicaoVM]:
        return ApiResponse(data=service.inativar(pessoa_id, identificador, admin.sub))

    def pessoa_profissao_service(
        unidade: Annotated[Session, Depends(sessao)],
    ) -> PessoaProfissaoService:
        return PessoaProfissaoService(unidade)

    @router.get("/pessoas/{pessoa_id}/profissoes", tags=["Vínculos e qualificações"])
    def listar_pessoa_profissao(
        pessoa_id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaProfissaoService, Depends(pessoa_profissao_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[PessoaProfissaoVM]]:
        return ApiResponse(data=service.listar(pessoa_id, limite, deslocamento, incluir_inativos))

    @router.get(
        "/pessoas/{pessoa_id}/profissoes/{identificador}", tags=["Vínculos e qualificações"]
    )
    def obter_pessoa_profissao(
        pessoa_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaProfissaoService, Depends(pessoa_profissao_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[PessoaProfissaoVM]:
        return ApiResponse(data=service.obter(pessoa_id, identificador, incluir_inativos))

    @router.post(
        "/pessoas/{pessoa_id}/profissoes", status_code=201, tags=["Vínculos e qualificações"]
    )
    def criar_pessoa_profissao(
        pessoa_id: UUID,
        dados: PessoaProfissaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaProfissaoService, Depends(pessoa_profissao_service)],
    ) -> ApiResponse[PessoaProfissaoVM]:
        return ApiResponse(data=service.criar(pessoa_id, dados, admin.sub))

    @router.put(
        "/pessoas/{pessoa_id}/profissoes/{identificador}", tags=["Vínculos e qualificações"]
    )
    def editar_pessoa_profissao(
        pessoa_id: UUID,
        identificador: UUID,
        dados: PessoaProfissaoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaProfissaoService, Depends(pessoa_profissao_service)],
    ) -> ApiResponse[PessoaProfissaoVM]:
        return ApiResponse(data=service.editar(pessoa_id, identificador, dados, admin.sub))

    @router.delete(
        "/pessoas/{pessoa_id}/profissoes/{identificador}", tags=["Vínculos e qualificações"]
    )
    def inativar_pessoa_profissao(
        pessoa_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaProfissaoService, Depends(pessoa_profissao_service)],
    ) -> ApiResponse[PessoaProfissaoVM]:
        return ApiResponse(data=service.inativar(pessoa_id, identificador, admin.sub))

    def pessoa_curso_service(unidade: Annotated[Session, Depends(sessao)]) -> PessoaCursoService:
        return PessoaCursoService(unidade)

    @router.get("/pessoas/{pessoa_id}/cursos", tags=["Vínculos e qualificações"])
    def listar_pessoa_curso(
        pessoa_id: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaCursoService, Depends(pessoa_curso_service)],
        limite: Annotated[int, Query(ge=1, le=100)] = 50,
        deslocamento: Annotated[int, Query(ge=0)] = 0,
        incluir_inativos: bool = False,
    ) -> ApiResponse[list[PessoaCursoVM]]:
        return ApiResponse(data=service.listar(pessoa_id, limite, deslocamento, incluir_inativos))

    @router.get("/pessoas/{pessoa_id}/cursos/{identificador}", tags=["Vínculos e qualificações"])
    def obter_pessoa_curso(
        pessoa_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaCursoService, Depends(pessoa_curso_service)],
        incluir_inativos: bool = False,
    ) -> ApiResponse[PessoaCursoVM]:
        return ApiResponse(data=service.obter(pessoa_id, identificador, incluir_inativos))

    @router.post("/pessoas/{pessoa_id}/cursos", status_code=201, tags=["Vínculos e qualificações"])
    def criar_pessoa_curso(
        pessoa_id: UUID,
        dados: PessoaCursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaCursoService, Depends(pessoa_curso_service)],
    ) -> ApiResponse[PessoaCursoVM]:
        return ApiResponse(data=service.criar(pessoa_id, dados, admin.sub))

    @router.put("/pessoas/{pessoa_id}/cursos/{identificador}", tags=["Vínculos e qualificações"])
    def editar_pessoa_curso(
        pessoa_id: UUID,
        identificador: UUID,
        dados: PessoaCursoInput,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaCursoService, Depends(pessoa_curso_service)],
    ) -> ApiResponse[PessoaCursoVM]:
        return ApiResponse(data=service.editar(pessoa_id, identificador, dados, admin.sub))

    @router.delete("/pessoas/{pessoa_id}/cursos/{identificador}", tags=["Vínculos e qualificações"])
    def inativar_pessoa_curso(
        pessoa_id: UUID,
        identificador: UUID,
        admin: Annotated[Principal, Depends(exigir_admin)],
        service: Annotated[PessoaCursoService, Depends(pessoa_curso_service)],
    ) -> ApiResponse[PessoaCursoVM]:
        return ApiResponse(data=service.inativar(pessoa_id, identificador, admin.sub))

    return router

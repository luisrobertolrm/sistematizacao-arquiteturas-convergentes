from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, ValidationError

from core.http.contratos import ErroNegocio
from web.settings import Settings

bearer: HTTPBearer = HTTPBearer(auto_error=False)


class Principal(BaseModel):
    sub: str = Field(min_length=1, max_length=200)
    role: str


def autenticacao(settings: Settings) -> Callable[..., Principal]:
    def exigir_admin(
        credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    ) -> Principal:
        if settings.jwt_secret is None:
            raise ErroNegocio(
                503, "Autenticação não configurada", "Configure o emissor e o segredo JWT."
            )
        if credenciais is None:
            raise ErroNegocio(401, "Não autenticado", "Informe um token Bearer válido.")
        try:
            principal: Principal = Principal.model_validate(
                jwt.decode(
                    credenciais.credentials,
                    settings.jwt_secret.get_secret_value(),
                    algorithms=["HS256"],
                    audience=settings.jwt_audience,
                    issuer=settings.jwt_issuer,
                    options={"require": ["sub", "exp", "iat", "iss", "aud"]},
                )
            )
        except (jwt.InvalidTokenError, ValidationError) as erro:
            raise ErroNegocio(401, "Não autenticado", "Token inválido ou expirado.") from erro
        if principal.role != "admin":
            raise ErroNegocio(403, "Acesso negado", "Esta operação exige perfil administrativo.")
        return principal

    return exigir_admin

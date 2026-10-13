from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from web.autenticacao.emitir_token import ClaimsEmitidos
from web.main import create_app
from web.settings import Settings

SEGREDO_TESTE: str = "segredo-exclusivo-de-teste-nao-usar-em-producao"


def token_teste(role: str = "admin", issuer: str = "teste", expira: int = 60) -> str:
    agora: datetime = datetime.now(UTC)
    claims: ClaimsEmitidos = {
        "sub": "administrador-teste",
        "role": role,
        "iss": issuer,
        "aud": "teste-api",
        "iat": int(agora.timestamp()),
        "exp": int((agora + timedelta(minutes=expira)).timestamp()),
    }
    return jwt.encode(dict(claims), SEGREDO_TESTE, algorithm="HS256")


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        environment="test",
        jwt_secret=SecretStr(SEGREDO_TESTE),
        jwt_issuer="teste",
        jwt_audience="teste-api",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings), raise_server_exceptions=False) as cliente:
        yield cliente

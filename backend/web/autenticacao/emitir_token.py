"""Emissor CLI para desenvolvimento. Não é endpoint nem mecanismo de login de produção."""

import argparse
from datetime import UTC, datetime, timedelta
from typing import TypedDict

import jwt

from web.settings import Settings


class ClaimsEmitidos(TypedDict):
    sub: str
    role: str
    iss: str
    aud: str
    iat: int
    exp: int


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--minutes", type=int, default=60)
    args: argparse.Namespace = parser.parse_args()
    settings: Settings = Settings()
    if settings.environment != "development" or settings.jwt_secret is None:
        parser.error("Disponível apenas em development, com REDE_JWT_SECRET configurado.")
    if not 1 <= args.minutes <= 480 or not 1 <= len(args.subject) <= 200:
        parser.error("Informe subject de 1–200 caracteres e validade de 1–480 minutos.")
    agora: datetime = datetime.now(UTC)
    claims: ClaimsEmitidos = {
        "sub": args.subject,
        "role": "admin",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(agora.timestamp()),
        "exp": int((agora + timedelta(minutes=args.minutes)).timestamp()),
    }
    print(jwt.encode(dict(claims), settings.jwt_secret.get_secret_value(), algorithm="HS256"))


if __name__ == "__main__":
    main()

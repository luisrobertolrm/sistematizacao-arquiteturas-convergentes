"""Gera configuração local sem sobrescrever arquivos ou imprimir segredos."""

import secrets
from pathlib import Path

from cryptography.fernet import Fernet


def main() -> int:
    raiz: Path = Path(__file__).resolve().parents[2]
    banco_env: Path = raiz / ".env"
    api_env: Path = raiz / "backend/.env"
    if banco_env.exists() or api_env.exists():
        print("Configuração já existe. Revise os arquivos .env existentes; nada foi sobrescrito.")
        return 1
    senha: str = secrets.token_hex(24)
    token_jwt: str = secrets.token_urlsafe(48)
    chave: str = Fernet.generate_key().decode("ascii")
    with banco_env.open("x", encoding="utf-8") as arquivo:
        arquivo.write(f"POSTGRES_PASSWORD={senha}\n")
    with api_env.open("x", encoding="utf-8") as arquivo:
        arquivo.write(
            "REDE_ENVIRONMENT=development\n"
            f"REDE_DATABASE_URL=postgresql+psycopg://redesolidaria:{senha}"
            "@localhost:55432/redesolidaria\n"
            f"REDE_JWT_SECRET={token_jwt}\n"
            "REDE_JWT_ISSUER=redesolidaria-local\n"
            "REDE_JWT_AUDIENCE=redesolidaria-api\n"
            'REDE_CORS_ORIGINS=["http://localhost:4200"]\n'
            f"REDE_ENCRYPTION_KEY={chave}\n"
        )
    print("Arquivos .env locais criados. Guarde-os fora do controle de versão.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

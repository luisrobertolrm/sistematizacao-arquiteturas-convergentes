from typing import Literal

from pydantic import Field, SecretStr, field_validator

from infra.database.settings import DatabaseSettings


class Settings(DatabaseSettings):
    environment: Literal["development", "test", "production"] = "development"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:4200"])
    jwt_secret: SecretStr | None = None
    jwt_issuer: str = "redesolidaria-local"
    jwt_audience: str = "redesolidaria-api"
    encryption_key: SecretStr | None = None
    encryption_key_id: str = Field(default="fernet-v1", min_length=1, max_length=100)
    ia_urls_permitidas: list[str] = Field(default_factory=list)

    @field_validator("jwt_secret", "encryption_key", mode="before")
    @classmethod
    def vazio_como_nulo(cls, valor: object) -> object:
        return None if valor == "" else valor

    @field_validator("jwt_secret")
    @classmethod
    def segredo_forte(cls, valor: SecretStr | None) -> SecretStr | None:
        if valor is not None and len(valor.get_secret_value()) < 32:
            raise ValueError("JWT secret deve ter pelo menos 32 caracteres aleatórios")
        return valor

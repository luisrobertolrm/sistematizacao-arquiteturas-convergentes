from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="REDE_", env_file=(".env", "env"), extra="ignore"
    )
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://redesolidaria@localhost:55432/redesolidaria"
    )


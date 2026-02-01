from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    PROJECT_NAME: str = "vr-admin"
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: str = "*"

    ADMIN_DEFAULT_LOCATION: str = "Другие Миры — Юго-Восток"
    DEFAULT_RESOURCE_NAME: str = "Арена 160 м?"

    def cors_list(self) -> list[str]:
        value = (self.CORS_ORIGINS or "").strip()
        if value == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()

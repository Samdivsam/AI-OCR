from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OCR Document Platform"
    environment: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ocr_db"
    jwt_secret_key: str = Field(..., min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    ocr_provider: Literal["local", "mock", "external"] = "local"
    ocr_api_url: str | None = None
    ocr_api_key: str | None = None
    max_upload_size_mb: int = 10
    allowed_origins: str = "http://localhost:3000"
    store_raw_ocr_text: bool = True
    extraction_version: str = "v1"
    http_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache

def get_settings() -> Settings:
    return Settings()


"""Application configuration.

Single source of truth for settings. Values come from environment variables,
optionally loaded from ``backend/.env`` during local development. Secrets are
never hard-coded here; only names and safe defaults live in this file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings, validated at startup."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "TestPilot AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    DEBUG: bool = True

    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        """CORS_ORIGINS as a clean list, skipping empty entries."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so settings are parsed once per process."""
    return Settings()


settings = get_settings()

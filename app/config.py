"""Application configuration via environment variables and pydantic-settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env file."""

    data_dir: Path = Field(default=Path("."), description="Directory containing Details.csv and Orders.csv")
    port: int = Field(default=8000, ge=1, le=65535, description="API server port")
    log_level: str = Field(default="INFO", description="Logging level")
    rate_limit: int = Field(default=120, ge=1, description="Max requests per minute per IP")
    rate_window_seconds: int = Field(default=60, ge=1, description="Rate limit window in seconds")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

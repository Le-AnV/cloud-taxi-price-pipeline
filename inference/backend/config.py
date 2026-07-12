"""Backend configuration for the NYC taxi fare inference service."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "NYC Taxi Fare Inference API"
    api_v1_prefix: str = "/api/v1"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    log_level: str = "INFO"

    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )
    nyc_boundary_geojson_path: Path = Path("assets/nyc_boundary.geojson")
    model_path: Path = Path("models/gradient_boosting_model_v3.pkl")
    fallback_model_path: Path = Path("models/random_forest_model_v3.pkl")
    osrm_base_url: AnyHttpUrl = "https://router.project-osrm.org"
    osrm_profile: str = "driving"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

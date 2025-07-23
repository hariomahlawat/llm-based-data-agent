from __future__ import annotations

from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    max_file_size: int = Field(5 * 1024 * 1024, env="MAX_FILE_SIZE")
    allowed_file_types: List[str] = Field(default_factory=lambda: ["csv", "xlsx"], env="ALLOWED_FILE_TYPES")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    safe_exec_mem_mb: int = Field(200, env="SAFE_EXEC_MEM_MB")

    class Config:
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()


settings = get_settings()

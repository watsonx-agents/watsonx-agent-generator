"""Configuration management using Pydantic Settings.

This module provides centralized configuration management with validation
and environment variable loading.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with automatic environment variable loading.

    This class uses Pydantic Settings to load and validate configuration
    from environment variables with fallback to defaults.

    Attributes:
        app_name: Application name for branding
        version: Current version of the application
        debug: Enable debug mode for verbose logging
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log output format (json or text)
        watsonx_apikey: IBM WatsonX API key (optional, for AI features)
        watsonx_url: IBM WatsonX API URL
        watsonx_project_id: IBM WatsonX project ID (optional)
        base_path: Base directory for the application
        assets_folder: Path to template assets
        output_folder: Default output directory for generated agents
        default_framework: Default framework to use when not specified
        default_port: Default port for generated agents
        max_workers: Maximum number of concurrent workers
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="WatsonX Agent Creator", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: Literal["json", "text"] = Field(
        default="json", description="Log output format"
    )

    # WatsonX AI settings
    watsonx_apikey: str | None = Field(
        default=None, description="IBM WatsonX API key", alias="WATSONX_APIKEY"
    )
    watsonx_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        description="IBM WatsonX API URL",
        alias="WATSONX_URL",
    )
    watsonx_project_id: str | None = Field(
        default=None, description="IBM WatsonX project ID", alias="PROJECT_ID"
    )

    # Paths
    base_path: Path = Field(
        default_factory=lambda: Path.cwd(), description="Base application directory"
    )
    assets_folder: Path = Field(
        default_factory=lambda: Path.cwd() / "assets",
        description="Template assets directory",
    )
    output_folder: Path = Field(
        default_factory=lambda: Path.cwd() / "agents",
        description="Output directory for generated agents",
    )

    # Generation defaults
    default_framework: str = Field(
        default="watsonx", description="Default framework for agent generation"
    )
    default_port: int = Field(
        default=8000, description="Default port for generated agents", ge=1000, le=65535
    )
    max_workers: int = Field(
        default=4, description="Maximum number of concurrent workers", ge=1, le=16
    )

    # AI Model settings
    model_id: str = Field(
        default="ibm/granite-13b-instruct-v2",
        description="WatsonX model ID for AI generation",
    )
    max_new_tokens: int = Field(
        default=4000, description="Maximum tokens for AI generation", ge=100, le=8000
    )
    temperature: float = Field(
        default=0.7, description="Temperature for AI generation", ge=0.0, le=2.0
    )

    @field_validator("base_path", "assets_folder", "output_folder", mode="before")
    @classmethod
    def resolve_paths(cls, v: str | Path) -> Path:
        """Resolve and validate path settings.

        Args:
            v: Path value to resolve

        Returns:
            Resolved Path object
        """
        if isinstance(v, str):
            v = Path(v)
        return v.expanduser().resolve()

    @field_validator("assets_folder")
    @classmethod
    def validate_assets_folder(cls, v: Path) -> Path:
        """Validate that assets folder exists.

        Args:
            v: Assets folder path

        Returns:
            Validated Path object

        Raises:
            ValueError: If assets folder doesn't exist
        """
        if not v.exists():
            raise ValueError(f"Assets folder not found: {v}")
        return v

    @property
    def has_watsonx_config(self) -> bool:
        """Check if WatsonX AI credentials are configured.

        Returns:
            True if API key and project ID are set, False otherwise
        """
        return bool(self.watsonx_apikey and self.watsonx_project_id)

    def ensure_output_folder(self) -> Path:
        """Ensure output folder exists, creating it if necessary.

        Returns:
            Path to the output folder

        Raises:
            OSError: If folder creation fails
        """
        self.output_folder.mkdir(parents=True, exist_ok=True)
        return self.output_folder


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance.

    This function uses LRU cache to ensure settings are loaded only once
    and reused throughout the application lifecycle.

    Returns:
        Cached Settings instance

    Examples:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        WatsonX Agent Creator
    """
    # Allow overriding base_path from environment or current directory
    base_path = os.getenv("WATSONX_BASE_PATH", Path.cwd())
    assets_folder = Path(base_path) / "assets"

    return Settings(
        base_path=base_path,
        assets_folder=assets_folder,
    )

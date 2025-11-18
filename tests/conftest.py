"""Pytest configuration and fixtures.

This module provides common fixtures and configuration for all tests.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from watsonx_agent_creator.core.config import Settings, get_settings
from watsonx_agent_creator.domain.models import (
    AgentConfig,
    DockerConfig,
    Framework,
    ProjectMetadata,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests.

    Yields:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def assets_dir(temp_dir: Path) -> Path:
    """Create mock assets directory.

    Args:
        temp_dir: Temporary directory path

    Returns:
        Path to assets directory
    """
    assets = temp_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    # Create framework directories
    for framework in ["watsonx", "langraph", "base"]:
        fw_dir = assets / "frameworks" / framework / "model"
        fw_dir.mkdir(parents=True, exist_ok=True)

        # Create sample agent.py
        agent_file = fw_dir / "agent.py"
        agent_file.write_text(
            '''"""Sample agent implementation."""


def run_agent():
    """Run the agent."""
    print("Agent running")
'''
        )

    # Create configs directory
    configs = assets / "configs"
    configs.mkdir(parents=True, exist_ok=True)

    # Create sample config files
    (configs / "logger.py").write_text("# Logger config\n")
    (configs / "settings.py").write_text("# Settings config\n")

    # Create main.py template
    (assets / "main.py").write_text(
        '''"""FastAPI application."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello"}
'''
    )

    return assets


@pytest.fixture
def test_settings(temp_dir: Path, assets_dir: Path) -> Settings:
    """Create test settings.

    Args:
        temp_dir: Temporary directory
        assets_dir: Assets directory

    Returns:
        Test settings instance
    """
    return Settings(
        base_path=temp_dir,
        assets_folder=assets_dir,
        output_folder=temp_dir / "agents",
        watsonx_apikey="test_api_key",
        watsonx_project_id="test_project_id",
    )


@pytest.fixture
def sample_metadata() -> ProjectMetadata:
    """Create sample project metadata.

    Returns:
        Sample ProjectMetadata instance
    """
    return ProjectMetadata(
        name="test_agent",
        display_name="Test Agent",
        description="A test agent",
        author="Test Author",
        author_email="test@example.com",
        framework=Framework.WATSONX,
    )


@pytest.fixture
def sample_docker_config() -> DockerConfig:
    """Create sample Docker configuration.

    Returns:
        Sample DockerConfig instance
    """
    return DockerConfig(
        host_port=8000,
        container_port=8000,
    )


@pytest.fixture
def sample_agent_config(
    temp_dir: Path,
    sample_metadata: ProjectMetadata,
    sample_docker_config: DockerConfig,
) -> AgentConfig:
    """Create sample agent configuration.

    Args:
        temp_dir: Temporary directory
        sample_metadata: Project metadata
        sample_docker_config: Docker configuration

    Returns:
        Sample AgentConfig instance
    """
    return AgentConfig(
        metadata=sample_metadata,
        output_path=temp_dir / "agents",
        docker=sample_docker_config,
        enable_ai_customization=False,
        git_init=False,
        install_dependencies=False,
    )


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    """Reset settings cache between tests.

    Yields:
        None
    """
    yield
    get_settings.cache_clear()

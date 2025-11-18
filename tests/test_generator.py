"""Tests for agent generator service.

This module tests the main agent generation workflow.
"""

import pytest

from watsonx_agent_creator.domain.models import AgentConfig
from watsonx_agent_creator.services.generator import AgentGenerator
from watsonx_agent_creator.services.template_service import TemplateService


class TestAgentGenerator:
    """Tests for AgentGenerator service."""

    @pytest.mark.asyncio
    async def test_generator_initialization(
        self,
        assets_dir,
    ) -> None:
        """Test generator initialization."""
        template_service = TemplateService(assets_path=assets_dir)
        generator = AgentGenerator(template_service=template_service)

        assert generator is not None
        assert generator.template_service is template_service

    @pytest.mark.asyncio
    async def test_generate_agent_basic(
        self,
        sample_agent_config: AgentConfig,
        assets_dir,
    ) -> None:
        """Test basic agent generation."""
        template_service = TemplateService(assets_path=assets_dir)
        generator = AgentGenerator(template_service=template_service)

        response = await generator.generate_agent(sample_agent_config)

        assert response.success
        assert response.agent_name == "test_agent"
        assert response.output_path.exists()

    @pytest.mark.asyncio
    async def test_generate_agent_creates_structure(
        self,
        sample_agent_config: AgentConfig,
        assets_dir,
    ) -> None:
        """Test that agent generation creates proper directory structure."""
        template_service = TemplateService(assets_path=assets_dir)
        generator = AgentGenerator(template_service=template_service)

        response = await generator.generate_agent(sample_agent_config)

        assert response.success

        # Check directory structure
        output_path = response.output_path
        assert (output_path / "app").exists()
        assert (output_path / "app" / "test_agent").exists()
        assert (output_path / "app" / "test_agent" / "configs").exists()
        assert (output_path / "app" / "test_agent" / "model").exists()
        assert (output_path / "tests").exists()

    @pytest.mark.asyncio
    async def test_generate_agent_creates_files(
        self,
        sample_agent_config: AgentConfig,
        assets_dir,
    ) -> None:
        """Test that agent generation creates necessary files."""
        template_service = TemplateService(assets_path=assets_dir)
        generator = AgentGenerator(template_service=template_service)

        response = await generator.generate_agent(sample_agent_config)

        assert response.success

        # Check key files
        output_path = response.output_path
        assert (output_path / "app" / "pyproject.toml").exists()
        assert (output_path / ".env.sample").exists()
        assert (output_path / "docker-compose.yml").exists()

    @pytest.mark.asyncio
    async def test_pyproject_toml_content(
        self,
        sample_agent_config: AgentConfig,
        assets_dir,
    ) -> None:
        """Test that generated pyproject.toml has correct content."""
        template_service = TemplateService(assets_path=assets_dir)
        generator = AgentGenerator(template_service=template_service)

        response = await generator.generate_agent(sample_agent_config)

        assert response.success

        # Read and validate pyproject.toml
        from watsonx_agent_creator.utils.file_operations import read_toml

        pyproject_path = response.output_path / "app" / "pyproject.toml"
        pyproject_data = read_toml(pyproject_path)

        assert "project" in pyproject_data
        assert pyproject_data["project"]["name"] == "test_agent"
        assert pyproject_data["project"]["version"] == "0.1.0"
        assert "dependencies" in pyproject_data["project"]

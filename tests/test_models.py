"""Tests for domain models.

This module tests Pydantic models with validation logic.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from watsonx_agent_creator.domain.models import (
    AgentConfig,
    AIModelConfig,
    DockerConfig,
    Framework,
    ProjectMetadata,
)


class TestFramework:
    """Tests for Framework enum."""

    def test_framework_values(self) -> None:
        """Test framework enum values."""
        assert Framework.WATSONX.value == "watsonx"
        assert Framework.LANGRAPH.value == "langraph"
        assert Framework.CREWAI.value == "crewai"
        assert Framework.BEEAI.value == "beeai"
        assert Framework.BASE.value == "base"

    def test_framework_display_name(self) -> None:
        """Test framework display names."""
        assert Framework.WATSONX.display_name == "IBM WatsonX SDK"
        assert Framework.LANGRAPH.display_name == "LangGraph"
        assert Framework.BASE.display_name == "Base (No Framework)"

    def test_framework_description(self) -> None:
        """Test framework descriptions."""
        assert "WatsonX.ai SDK" in Framework.WATSONX.description
        assert "stateful" in Framework.LANGRAPH.description


class TestProjectMetadata:
    """Tests for ProjectMetadata model."""

    def test_valid_metadata(self) -> None:
        """Test creating valid metadata."""
        metadata = ProjectMetadata(
            name="my_agent",
            display_name="My Agent",
            author="John Doe",
            author_email="john@example.com",
            framework=Framework.WATSONX,
        )

        assert metadata.name == "my_agent"
        assert metadata.display_name == "My Agent"
        assert metadata.author == "John Doe"
        assert metadata.version == "0.1.0"

    def test_invalid_name_uppercase(self) -> None:
        """Test that uppercase names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectMetadata(
                name="MyAgent",
                display_name="My Agent",
                author="John Doe",
                author_email="john@example.com",
                framework=Framework.WATSONX,
            )

        assert "lowercase" in str(exc_info.value).lower()

    def test_invalid_name_starts_with_underscore(self) -> None:
        """Test that names starting with underscore are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectMetadata(
                name="_agent",
                display_name="Agent",
                author="John Doe",
                author_email="john@example.com",
                framework=Framework.WATSONX,
            )

        assert "underscore" in str(exc_info.value).lower()

    def test_invalid_name_consecutive_underscores(self) -> None:
        """Test that consecutive underscores are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectMetadata(
                name="my__agent",
                display_name="My Agent",
                author="John Doe",
                author_email="john@example.com",
                framework=Framework.WATSONX,
            )

        assert "consecutive" in str(exc_info.value).lower()

    def test_invalid_email(self) -> None:
        """Test that invalid email is rejected."""
        with pytest.raises(ValidationError):
            ProjectMetadata(
                name="my_agent",
                display_name="My Agent",
                author="John Doe",
                author_email="invalid-email",
                framework=Framework.WATSONX,
            )

    def test_invalid_version(self) -> None:
        """Test that invalid version is rejected."""
        with pytest.raises(ValidationError):
            ProjectMetadata(
                name="my_agent",
                display_name="My Agent",
                author="John Doe",
                author_email="john@example.com",
                framework=Framework.WATSONX,
                version="1.0",  # Invalid - should be semver
            )


class TestAIModelConfig:
    """Tests for AIModelConfig model."""

    def test_valid_config(self) -> None:
        """Test creating valid AI model config."""
        config = AIModelConfig(
            model_id="ibm/granite-13b-instruct-v2",
            max_new_tokens=2000,
            temperature=0.7,
        )

        assert config.model_id == "ibm/granite-13b-instruct-v2"
        assert config.max_new_tokens == 2000
        assert config.temperature == 0.7

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = AIModelConfig()

        assert config.model_id == "ibm/granite-13b-instruct-v2"
        assert config.max_new_tokens == 4000
        assert config.temperature == 0.7
        assert config.top_p == 1.0
        assert config.top_k == 50

    def test_invalid_temperature_too_low(self) -> None:
        """Test that temperature below 0 is rejected."""
        with pytest.raises(ValidationError):
            AIModelConfig(temperature=-0.1)

    def test_invalid_temperature_too_high(self) -> None:
        """Test that temperature above 2.0 is rejected."""
        with pytest.raises(ValidationError):
            AIModelConfig(temperature=2.5)

    def test_invalid_max_tokens_too_low(self) -> None:
        """Test that max_new_tokens below 100 is rejected."""
        with pytest.raises(ValidationError):
            AIModelConfig(max_new_tokens=50)


class TestDockerConfig:
    """Tests for DockerConfig model."""

    def test_valid_config(self) -> None:
        """Test creating valid Docker config."""
        config = DockerConfig(
            host_port=8080,
            container_port=8000,
        )

        assert config.host_port == 8080
        assert config.container_port == 8000

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = DockerConfig()

        assert config.host_port == 8000
        assert config.container_port == 8000
        assert config.python_version == "3.12"

    def test_invalid_port_too_low(self) -> None:
        """Test that ports below 1000 are rejected."""
        with pytest.raises(ValidationError):
            DockerConfig(host_port=80)

    def test_invalid_port_too_high(self) -> None:
        """Test that ports above 65535 are rejected."""
        with pytest.raises(ValidationError):
            DockerConfig(host_port=70000)


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_valid_config(self, sample_agent_config: AgentConfig) -> None:
        """Test creating valid agent config."""
        assert sample_agent_config.metadata.name == "test_agent"
        assert sample_agent_config.docker.host_port == 8000
        assert not sample_agent_config.enable_ai_customization

    def test_path_resolution(self, tmp_path: Path) -> None:
        """Test that paths are properly resolved."""
        metadata = ProjectMetadata(
            name="test_agent",
            display_name="Test Agent",
            author="Test",
            author_email="test@example.com",
            framework=Framework.WATSONX,
        )

        config = AgentConfig(
            metadata=metadata,
            output_path="~/agents",  # Should be expanded
        )

        assert config.output_path.is_absolute()
        assert "~" not in str(config.output_path)

    def test_ai_customization_requires_task(self) -> None:
        """Test that AI customization requires custom_task."""
        metadata = ProjectMetadata(
            name="test_agent",
            display_name="Test Agent",
            author="Test",
            author_email="test@example.com",
            framework=Framework.WATSONX,
        )

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(
                metadata=metadata,
                output_path=Path("/tmp/agents"),
                enable_ai_customization=True,
                custom_task="",  # Empty task with AI enabled
            )

        assert "custom_task" in str(exc_info.value).lower()

    def test_to_dict_method(self, sample_agent_config: AgentConfig) -> None:
        """Test conversion to dictionary."""
        data = sample_agent_config.to_dict()

        assert data["agent_name"] == "test_agent"
        assert data["display_name"] == "Test Agent"
        assert data["author"] == "Test Author"
        assert data["framework"] == "watsonx"
        assert data["host_port"] == 8000

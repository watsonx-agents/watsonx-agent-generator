"""Domain models using Pydantic V2 for strict validation.

This module defines the core business models with comprehensive validation
and type safety using Pydantic V2.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Framework(str, Enum):
    """Supported AI agent frameworks.

    Each framework provides different capabilities and abstractions for
    building AI agents with IBM WatsonX.

    Attributes:
        WATSONX: Native IBM WatsonX SDK
        LANGRAPH: LangGraph framework for stateful agents
        CREWAI: CrewAI framework for multi-agent systems
        BEEAI: BeeAI framework for agent orchestration
        LANGFLOW: LangFlow visual programming for agents
        BASE: Minimal base template without framework
    """

    WATSONX = "watsonx"
    LANGRAPH = "langraph"
    CREWAI = "crewai"
    BEEAI = "beeai"
    LANGFLOW = "langflow"
    BASE = "base"

    @property
    def display_name(self) -> str:
        """Get human-readable framework name.

        Returns:
            Formatted framework name
        """
        names = {
            self.WATSONX: "IBM WatsonX SDK",
            self.LANGRAPH: "LangGraph",
            self.CREWAI: "CrewAI",
            self.BEEAI: "BeeAI Framework",
            self.LANGFLOW: "LangFlow",
            self.BASE: "Base (No Framework)",
        }
        return names.get(self, self.value.title())

    @property
    def description(self) -> str:
        """Get framework description.

        Returns:
            Framework description text
        """
        descriptions = {
            self.WATSONX: "Native IBM WatsonX.ai SDK for direct model access",
            self.LANGRAPH: "Build stateful, multi-actor applications with LLMs",
            self.CREWAI: "Framework for orchestrating role-playing autonomous AI agents",
            self.BEEAI: "Production-ready agent framework with observability",
            self.LANGFLOW: "Visual programming interface for LangChain",
            self.BASE: "Minimal template for custom implementations",
        }
        return descriptions.get(self, "")


class ProjectMetadata(BaseModel):
    """Metadata for generated agent project.

    Attributes:
        name: Project name (snake_case)
        display_name: Human-readable project name
        description: Project description
        author: Project author name
        author_email: Project author email
        version: Initial project version
        license: Project license
        created_at: Project creation timestamp
        framework: Framework used in the project
    """

    model_config = {"frozen": True, "str_strip_whitespace": True}

    name: str = Field(
        ...,
        description="Project name in snake_case",
        min_length=3,
        max_length=50,
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    display_name: str = Field(..., description="Human-readable project name", min_length=3)
    description: str = Field(default="", description="Project description", max_length=500)
    author: str = Field(..., description="Project author name", min_length=2)
    author_email: str = Field(..., description="Project author email", pattern=r"^[^@]+@[^@]+\.[^@]+$")
    version: str = Field(default="0.1.0", description="Project version", pattern=r"^\d+\.\d+\.\d+$")
    license: str = Field(default="Apache-2.0", description="Project license")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    framework: Framework = Field(..., description="Framework to use")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name format.

        Args:
            v: Project name to validate

        Returns:
            Validated project name

        Raises:
            ValueError: If name format is invalid
        """
        if not v.islower():
            raise ValueError("Project name must be lowercase")
        if v.startswith("_") or v.endswith("_"):
            raise ValueError("Project name cannot start or end with underscore")
        if "__" in v:
            raise ValueError("Project name cannot contain consecutive underscores")
        return v


class AIModelConfig(BaseModel):
    """Configuration for AI model used in agent generation.

    Attributes:
        model_id: WatsonX model identifier
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 2.0)
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
        repetition_penalty: Penalty for token repetition
    """

    model_config = {"frozen": True}

    model_id: str = Field(
        default="ibm/granite-13b-instruct-v2",
        description="WatsonX model ID",
    )
    max_new_tokens: int = Field(
        default=4000,
        description="Maximum tokens to generate",
        ge=100,
        le=8000,
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature",
        ge=0.0,
        le=2.0,
    )
    top_p: float = Field(
        default=1.0,
        description="Nucleus sampling parameter",
        ge=0.0,
        le=1.0,
    )
    top_k: int = Field(
        default=50,
        description="Top-k sampling parameter",
        ge=1,
        le=100,
    )
    repetition_penalty: float = Field(
        default=1.0,
        description="Repetition penalty",
        ge=1.0,
        le=2.0,
    )


class DockerConfig(BaseModel):
    """Docker configuration for generated agent.

    Attributes:
        host_port: Port to expose on host machine
        container_port: Port inside container
        python_version: Python version for Docker image
        base_image: Base Docker image
    """

    model_config = {"frozen": True}

    host_port: int = Field(
        default=8000,
        description="Host port for agent service",
        ge=1000,
        le=65535,
    )
    container_port: int = Field(
        default=8000,
        description="Container port",
        ge=1000,
        le=65535,
    )
    python_version: str = Field(
        default="3.12",
        description="Python version",
        pattern=r"^3\.(11|12)$",
    )
    base_image: str = Field(
        default="python:3.12-slim",
        description="Base Docker image",
    )

    @model_validator(mode="after")
    def validate_ports(self) -> "DockerConfig":
        """Validate port configuration.

        Returns:
            Validated DockerConfig instance

        Raises:
            ValueError: If port configuration is invalid
        """
        if self.host_port == self.container_port:
            # This is fine - direct mapping
            pass
        elif abs(self.host_port - self.container_port) > 1000:
            raise ValueError("Host and container ports should be relatively close")
        return self


class AgentConfig(BaseModel):
    """Complete configuration for agent generation.

    This model combines all configuration aspects needed to generate
    a complete agent project.

    Attributes:
        metadata: Project metadata
        output_path: Output directory path
        docker: Docker configuration
        ai_model: AI model configuration (optional)
        enable_ai_customization: Whether to use AI for code customization
        custom_task: Custom task description for AI customization
        git_init: Initialize git repository
        install_dependencies: Install dependencies after generation
    """

    metadata: ProjectMetadata = Field(..., description="Project metadata")
    output_path: Path = Field(..., description="Output directory path")
    docker: DockerConfig = Field(default_factory=DockerConfig, description="Docker configuration")
    ai_model: AIModelConfig | None = Field(
        default=None,
        description="AI model configuration",
    )
    enable_ai_customization: bool = Field(
        default=False,
        description="Enable AI-powered customization",
    )
    custom_task: str = Field(
        default="",
        description="Custom task description for AI",
        max_length=1000,
    )
    git_init: bool = Field(
        default=True,
        description="Initialize git repository",
    )
    install_dependencies: bool = Field(
        default=True,
        description="Install dependencies using UV",
    )

    @field_validator("output_path", mode="before")
    @classmethod
    def resolve_path(cls, v: str | Path) -> Path:
        """Resolve output path.

        Args:
            v: Path to resolve

        Returns:
            Resolved Path object
        """
        if isinstance(v, str):
            v = Path(v)
        return v.expanduser().resolve()

    @model_validator(mode="after")
    def validate_ai_config(self) -> "AgentConfig":
        """Validate AI configuration consistency.

        Returns:
            Validated AgentConfig instance

        Raises:
            ValueError: If AI configuration is inconsistent
        """
        if self.enable_ai_customization:
            if not self.ai_model:
                # Create default AI model config
                object.__setattr__(self, "ai_model", AIModelConfig())
            if not self.custom_task:
                raise ValueError("custom_task is required when enable_ai_customization is True")
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary for template rendering.

        Returns:
            Dictionary representation suitable for templates
        """
        return {
            "agent_name": self.metadata.name,
            "display_name": self.metadata.display_name,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "author_email": self.metadata.author_email,
            "version": self.metadata.version,
            "license": self.metadata.license,
            "framework": self.metadata.framework.value,
            "framework_display": self.metadata.framework.display_name,
            "host_port": self.docker.host_port,
            "container_port": self.docker.container_port,
            "python_version": self.docker.python_version,
            "year": datetime.now().year,
        }

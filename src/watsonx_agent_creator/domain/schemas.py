"""API schemas and DTOs for request/response handling.

This module defines data transfer objects (DTOs) used for API communication
and user interaction.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from watsonx_agent_creator.domain.models import Framework


class FrameworkInfo(BaseModel):
    """Information about an available framework.

    Attributes:
        id: Framework identifier
        name: Human-readable framework name
        description: Framework description
        dependencies: Required Python packages
        available: Whether framework is available/supported
    """

    id: Framework = Field(..., description="Framework identifier")
    name: str = Field(..., description="Framework display name")
    description: str = Field(..., description="Framework description")
    dependencies: list[str] = Field(default_factory=list, description="Required packages")
    available: bool = Field(default=True, description="Framework availability")

    @classmethod
    def from_framework(cls, framework: Framework) -> "FrameworkInfo":
        """Create FrameworkInfo from Framework enum.

        Args:
            framework: Framework enum value

        Returns:
            FrameworkInfo instance
        """
        # Default dependencies for each framework
        deps_map = {
            Framework.WATSONX: ["ibm-watsonx-ai>=1.3.11"],
            Framework.LANGRAPH: ["langgraph>=0.3.34", "langchain-ibm==0.3.10"],
            Framework.CREWAI: ["crewai>=0.1.0"],
            Framework.BEEAI: ["beeai-framework>=0.1.14"],
            Framework.LANGFLOW: ["langflow>=0.5.0"],
            Framework.BASE: [],
        }

        return cls(
            id=framework,
            name=framework.display_name,
            description=framework.description,
            dependencies=deps_map.get(framework, []),
        )


class AgentGenerationRequest(BaseModel):
    """Request model for agent generation.

    Attributes:
        name: Agent project name (snake_case)
        framework: Framework to use
        output_path: Output directory path
        author: Author name
        author_email: Author email
        description: Project description
        port: Host port for agent service
        enable_ai: Enable AI-powered customization
        custom_task: Custom task for AI customization
        git_init: Initialize git repository
    """

    name: str = Field(
        ...,
        description="Agent project name",
        min_length=3,
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    framework: Framework = Field(
        default=Framework.WATSONX,
        description="Framework to use",
    )
    output_path: Path = Field(
        default=Path("./agents"),
        description="Output directory",
    )
    author: str = Field(
        default="Developer",
        description="Author name",
    )
    author_email: str = Field(
        default="dev@example.com",
        description="Author email",
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
    )
    description: str = Field(
        default="",
        description="Project description",
        max_length=500,
    )
    port: int = Field(
        default=8000,
        description="Host port",
        ge=1000,
        le=65535,
    )
    enable_ai: bool = Field(
        default=False,
        description="Enable AI customization",
    )
    custom_task: str = Field(
        default="",
        description="Custom task description",
        max_length=1000,
    )
    git_init: bool = Field(
        default=True,
        description="Initialize git repository",
    )


class AgentGenerationResponse(BaseModel):
    """Response model for agent generation.

    Attributes:
        success: Whether generation was successful
        agent_name: Name of generated agent
        output_path: Path to generated project
        framework: Framework used
        message: Status message
        error: Error message if failed
        metadata: Additional generation metadata
    """

    success: bool = Field(..., description="Generation success status")
    agent_name: str = Field(..., description="Generated agent name")
    output_path: Path = Field(..., description="Output path")
    framework: Framework = Field(..., description="Framework used")
    message: str = Field(..., description="Status message")
    error: str | None = Field(default=None, description="Error message if failed")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            Path: str,
        }

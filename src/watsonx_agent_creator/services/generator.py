"""Main agent generation service.

This module orchestrates the complete agent project generation process,
coordinating template rendering, file operations, and AI customization.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Any

from watsonx_agent_creator.core.config import get_settings
from watsonx_agent_creator.core.exceptions import GenerationError
from watsonx_agent_creator.core.logging import get_logger
from watsonx_agent_creator.domain.models import AgentConfig, Framework
from watsonx_agent_creator.domain.schemas import AgentGenerationResponse
from watsonx_agent_creator.services.ai_service import AIService
from watsonx_agent_creator.services.template_service import TemplateService
from watsonx_agent_creator.utils.file_operations import (
    copy_directory,
    copy_file,
    ensure_directory,
    read_toml,
    write_file,
    write_toml,
)

logger = get_logger(__name__)


class AgentGenerator:
    """Main service for generating AI agent projects.

    This service orchestrates the complete agent generation workflow including:
    - Template selection and rendering
    - File structure creation
    - Dependency management
    - Optional AI-powered customization
    - Git initialization
    - Dependency installation

    Attributes:
        settings: Application settings
        template_service: Template rendering service
        ai_service: Optional AI service for code customization
    """

    def __init__(
        self,
        template_service: TemplateService | None = None,
        ai_service: AIService | None = None,
    ) -> None:
        """Initialize the generator service.

        Args:
            template_service: Optional template service (creates default if None)
            ai_service: Optional AI service for customization

        Examples:
            >>> generator = AgentGenerator()
            >>> response = await generator.generate_agent(config)
        """
        self.settings = get_settings()
        self.template_service = template_service or TemplateService()
        self.ai_service = ai_service

        logger.info("Agent generator initialized")

    async def generate_agent(self, config: AgentConfig) -> AgentGenerationResponse:
        """Generate complete agent project.

        This is the main entry point for agent generation. It coordinates
        all steps of the generation process.

        Args:
            config: Agent configuration

        Returns:
            Generation response with status and metadata

        Raises:
            GenerationError: If generation fails

        Examples:
            >>> config = AgentConfig(...)
            >>> generator = AgentGenerator()
            >>> response = await generator.generate_agent(config)
            >>> print(response.message)
        """
        logger.info(f"Starting agent generation: {config.metadata.name}")

        try:
            # Calculate output path
            output_path = config.output_path / config.metadata.name
            ensure_directory(output_path)

            # Create project structure
            await self._create_project_structure(config, output_path)

            # Copy framework templates
            await self._copy_framework_templates(config, output_path)

            # Generate configuration files
            await self._generate_config_files(config, output_path)

            # Generate code files
            await self._generate_code_files(config, output_path)

            # Optional AI customization
            if config.enable_ai_customization and self.ai_service:
                await self._apply_ai_customization(config, output_path)

            # Initialize git repository
            if config.git_init:
                await self._initialize_git(output_path)

            # Install dependencies
            if config.install_dependencies:
                await self._install_dependencies(output_path)

            logger.info(f"Agent generation completed: {config.metadata.name}")

            return AgentGenerationResponse(
                success=True,
                agent_name=config.metadata.name,
                output_path=output_path,
                framework=config.metadata.framework,
                message=f"✨ Agent '{config.metadata.name}' generated successfully!",
                metadata={
                    "framework": config.metadata.framework.value,
                    "port": config.docker.host_port,
                    "ai_customization": config.enable_ai_customization,
                },
            )

        except Exception as e:
            logger.error(f"Agent generation failed: {e}", exc_info=True)
            return AgentGenerationResponse(
                success=False,
                agent_name=config.metadata.name,
                output_path=config.output_path,
                framework=config.metadata.framework,
                message="❌ Agent generation failed",
                error=str(e),
            )

    async def _create_project_structure(
        self,
        config: AgentConfig,
        output_path: Path,
    ) -> None:
        """Create basic project directory structure.

        Args:
            config: Agent configuration
            output_path: Project output path
        """
        logger.debug("Creating project structure")

        # Create main directories
        directories = [
            output_path / "app",
            output_path / "app" / config.metadata.name,
            output_path / "app" / config.metadata.name / "configs",
            output_path / "app" / config.metadata.name / "model",
            output_path / "tests",
        ]

        for directory in directories:
            ensure_directory(directory)

        logger.debug(f"Created {len(directories)} directories")

    async def _copy_framework_templates(
        self,
        config: AgentConfig,
        output_path: Path,
    ) -> None:
        """Copy framework-specific templates.

        Args:
            config: Agent configuration
            output_path: Project output path
        """
        logger.debug(f"Copying framework templates: {config.metadata.framework.value}")

        framework_path = (
            self.settings.assets_folder / "frameworks" / config.metadata.framework.value
        )

        if not framework_path.exists():
            raise GenerationError(
                f"Framework templates not found: {config.metadata.framework.value}",
                {"framework": config.metadata.framework.value, "path": str(framework_path)},
            )

        # Copy model templates if they exist
        model_src = framework_path / "model"
        if model_src.exists():
            model_dst = output_path / "app" / config.metadata.name / "model"
            copy_directory(
                model_src,
                model_dst,
                ignore_patterns=["__pycache__", "*.pyc", ".DS_Store"],
            )

        logger.debug("Framework templates copied")

    async def _generate_config_files(
        self,
        config: AgentConfig,
        output_path: Path,
    ) -> None:
        """Generate configuration files (pyproject.toml, .env, etc.).

        Args:
            config: Agent configuration
            output_path: Project output path
        """
        logger.debug("Generating configuration files")

        context = config.to_dict()

        # Generate pyproject.toml
        pyproject_data = self._build_pyproject_toml(config)
        write_toml(output_path / "app" / "pyproject.toml", pyproject_data)

        # Generate .env.sample
        env_content = self._build_env_file(config)
        await write_file(output_path / ".env.sample", env_content)

        # Generate README.md
        if self.template_service.template_exists("README.md.j2"):
            readme_content = self.template_service.render_template("README.md.j2", context)
            await write_file(output_path / "README.md", readme_content)

        # Generate Dockerfile
        if self.template_service.template_exists("Dockerfile.j2"):
            dockerfile_content = self.template_service.render_template("Dockerfile.j2", context)
            await write_file(output_path / "Dockerfile", dockerfile_content)
        elif (self.settings.assets_folder / "Dockerfile").exists():
            copy_file(
                self.settings.assets_folder / "Dockerfile",
                output_path / "Dockerfile",
            )

        # Generate docker-compose.yml
        compose_content = self._build_compose_file(config)
        await write_file(output_path / "docker-compose.yml", compose_content)

        logger.debug("Configuration files generated")

    async def _generate_code_files(
        self,
        config: AgentConfig,
        output_path: Path,
    ) -> None:
        """Generate Python code files.

        Args:
            config: Agent configuration
            output_path: Project output path
        """
        logger.debug("Generating code files")

        context = config.to_dict()
        app_path = output_path / "app" / config.metadata.name

        # Copy configs templates
        configs_src = self.settings.assets_folder / "configs"
        configs_dst = app_path / "configs"

        if configs_src.exists():
            copy_directory(
                configs_src,
                configs_dst,
                ignore_patterns=["__pycache__", "*.pyc"],
            )

        # Generate main.py
        main_src = self.settings.assets_folder / "main.py"
        if main_src.exists():
            copy_file(main_src, output_path / "app" / config.metadata.name / "main.py")

        # Generate __init__.py files
        init_files = [
            app_path / "__init__.py",
            app_path / "configs" / "__init__.py",
            app_path / "model" / "__init__.py",
            output_path / "tests" / "__init__.py",
        ]

        for init_file in init_files:
            if not init_file.exists():
                await write_file(init_file, '"""Package initialization."""\n')

        logger.debug("Code files generated")

    async def _apply_ai_customization(
        self,
        config: AgentConfig,
        output_path: Path,
    ) -> None:
        """Apply AI-powered code customization.

        Args:
            config: Agent configuration
            output_path: Project output path
        """
        if not self.ai_service:
            logger.warning("AI service not available, skipping customization")
            return

        logger.info("Applying AI customization")

        # Find agent.py file
        agent_file = output_path / "app" / config.metadata.name / "model" / "agent.py"

        if not agent_file.exists():
            logger.warning(f"Agent file not found: {agent_file}")
            return

        # Read base code
        async with asyncio.open_file(agent_file, "r") as f:
            base_code = await f.read()

        # Generate customized code
        customized_code = await self.ai_service.generate_agent_code(
            task_description=config.custom_task,
            base_code=base_code,
            framework=config.metadata.framework.value,
        )

        # Validate code
        is_valid = await self.ai_service.validate_code(customized_code)

        if is_valid:
            # Write customized code
            await write_file(agent_file, customized_code)
            logger.info("AI customization applied successfully")
        else:
            logger.warning("Generated code is invalid, keeping original")

    async def _initialize_git(self, output_path: Path) -> None:
        """Initialize git repository.

        Args:
            output_path: Project output path
        """
        logger.debug("Initializing git repository")

        try:
            # Initialize git
            subprocess.run(
                ["git", "init"],
                cwd=output_path,
                check=True,
                capture_output=True,
            )

            # Create .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
"""
            await write_file(output_path / ".gitignore", gitignore_content)

            logger.debug("Git repository initialized")

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to initialize git: {e}")
        except FileNotFoundError:
            logger.warning("Git not found, skipping initialization")

    async def _install_dependencies(self, output_path: Path) -> None:
        """Install project dependencies using UV.

        Args:
            output_path: Project output path
        """
        logger.info("Installing dependencies with UV")

        try:
            app_path = output_path / "app"

            # Run uv sync
            result = subprocess.run(
                ["uv", "pip", "install", "-e", "."],
                cwd=app_path,
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("Dependencies installed successfully")
            else:
                logger.warning(f"Dependency installation had issues: {result.stderr}")

        except FileNotFoundError:
            logger.warning("UV not found, skipping dependency installation")
        except Exception as e:
            logger.warning(f"Failed to install dependencies: {e}")

    def _build_pyproject_toml(self, config: AgentConfig) -> dict[str, Any]:
        """Build pyproject.toml configuration.

        Args:
            config: Agent configuration

        Returns:
            Pyproject configuration dictionary
        """
        # Load framework dependencies if available
        framework_deps = self._get_framework_dependencies(config.metadata.framework)

        return {
            "project": {
                "name": config.metadata.name,
                "version": config.metadata.version,
                "description": config.metadata.description or f"{config.metadata.display_name} AI Agent",
                "authors": [
                    {"name": config.metadata.author, "email": config.metadata.author_email}
                ],
                "license": {"text": config.metadata.license},
                "requires-python": ">=3.11,<3.13",
                "dependencies": [
                    "fastapi>=0.115.0",
                    "uvicorn>=0.32.0",
                    "pydantic>=2.8.0",
                    "python-dotenv>=1.0.1",
                    *framework_deps,
                ],
            },
            "build-system": {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build",
            },
        }

    def _get_framework_dependencies(self, framework: Framework) -> list[str]:
        """Get framework-specific dependencies.

        Args:
            framework: Framework enum

        Returns:
            List of dependency specifications
        """
        deps_map = {
            Framework.WATSONX: ["ibm-watsonx-ai>=1.3.11"],
            Framework.LANGRAPH: ["langgraph>=0.3.34", "langchain-ibm==0.3.10"],
            Framework.CREWAI: ["crewai>=0.1.0"],
            Framework.BEEAI: ["beeai-framework>=0.1.14"],
            Framework.LANGFLOW: ["langflow>=0.5.0"],
            Framework.BASE: [],
        }
        return deps_map.get(framework, [])

    def _build_env_file(self, config: AgentConfig) -> str:
        """Build .env file content.

        Args:
            config: Agent configuration

        Returns:
            Environment file content
        """
        return f"""# {config.metadata.display_name} Configuration

# WatsonX Configuration
WATSONX_APIKEY=your_api_key_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
PROJECT_ID=your_project_id_here

# Application Settings
APP_NAME={config.metadata.name}
APP_VERSION={config.metadata.version}
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT={config.docker.container_port}
"""

    def _build_compose_file(self, config: AgentConfig) -> str:
        """Build docker-compose.yml content.

        Args:
            config: Agent configuration

        Returns:
            Docker Compose file content
        """
        return f"""version: '3.8'

services:
  {config.metadata.name}:
    build: .
    container_name: {config.metadata.name}
    ports:
      - "{config.docker.host_port}:{config.docker.container_port}"
    environment:
      - WATSONX_APIKEY=${{WATSONX_APIKEY}}
      - WATSONX_URL=${{WATSONX_URL}}
      - PROJECT_ID=${{PROJECT_ID}}
    env_file:
      - .env
    volumes:
      - ./app:/app
    restart: unless-stopped
"""

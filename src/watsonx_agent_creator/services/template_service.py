"""Template rendering service using Jinja2.

This module provides template rendering capabilities with support for
both file-based and string-based templates.
"""

from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    Template,
    TemplateError as Jinja2TemplateError,
    TemplateNotFound,
)

from watsonx_agent_creator.core.config import get_settings
from watsonx_agent_creator.core.exceptions import TemplateError
from watsonx_agent_creator.core.logging import get_logger

logger = get_logger(__name__)


class TemplateService:
    """Service for rendering Jinja2 templates.

    This service provides methods for rendering templates from files or strings
    with proper error handling and logging.

    Attributes:
        env: Jinja2 environment instance
        assets_path: Path to template assets directory
    """

    def __init__(self, assets_path: Path | None = None) -> None:
        """Initialize the template service.

        Args:
            assets_path: Optional path to assets directory (defaults to settings)

        Examples:
            >>> service = TemplateService()
            >>> content = service.render_template("main.py.j2", {"name": "my_agent"})
        """
        settings = get_settings()
        self.assets_path = assets_path or settings.assets_folder

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.assets_path)),
            autoescape=False,  # We're generating code, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["snake_case"] = self._snake_case_filter
        self.env.filters["title_case"] = self._title_case_filter

        logger.info(f"Template service initialized with assets path: {self.assets_path}")

    @staticmethod
    def _snake_case_filter(text: str) -> str:
        """Convert text to snake_case.

        Args:
            text: Text to convert

        Returns:
            Snake-cased text
        """
        import re

        # Replace spaces and hyphens with underscores
        text = text.replace(" ", "_").replace("-", "_")
        # Insert underscore before uppercase letters
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
        return text.lower()

    @staticmethod
    def _title_case_filter(text: str) -> str:
        """Convert text to Title Case.

        Args:
            text: Text to convert

        Returns:
            Title-cased text
        """
        return text.replace("_", " ").replace("-", " ").title()

    def render_template(
        self,
        template_name: str,
        context: dict[str, Any],
    ) -> str:
        """Render a template file with the given context.

        Args:
            template_name: Name of template file (relative to assets_path)
            context: Context dictionary for template rendering

        Returns:
            Rendered template as string

        Raises:
            TemplateError: If template rendering fails

        Examples:
            >>> service = TemplateService()
            >>> content = service.render_template(
            ...     "README.md.j2",
            ...     {"name": "my_agent", "author": "John Doe"}
            ... )
        """
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**context)
            logger.debug(f"Rendered template: {template_name}")
            return rendered
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}")
            raise TemplateError(
                f"Template not found: {template_name}",
                {"template": template_name, "assets_path": str(self.assets_path)},
            ) from e
        except Jinja2TemplateError as e:
            logger.error(f"Template rendering error: {template_name}", exc_info=True)
            raise TemplateError(
                f"Failed to render template: {template_name}",
                {"template": template_name, "error": str(e)},
            ) from e

    def render_string(self, template_str: str, context: dict[str, Any]) -> str:
        """Render a template string with the given context.

        Args:
            template_str: Template string to render
            context: Context dictionary for template rendering

        Returns:
            Rendered template as string

        Raises:
            TemplateError: If template rendering fails

        Examples:
            >>> service = TemplateService()
            >>> content = service.render_string(
            ...     "Hello {{ name }}!",
            ...     {"name": "World"}
            ... )
            'Hello World!'
        """
        try:
            template = self.env.from_string(template_str)
            rendered = template.render(**context)
            logger.debug("Rendered template string")
            return rendered
        except Jinja2TemplateError as e:
            logger.error("Template string rendering error", exc_info=True)
            raise TemplateError(
                "Failed to render template string",
                {"error": str(e)},
            ) from e

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists.

        Args:
            template_name: Name of template file

        Returns:
            True if template exists, False otherwise

        Examples:
            >>> service = TemplateService()
            >>> if service.template_exists("main.py.j2"):
            ...     content = service.render_template("main.py.j2", context)
        """
        template_path = self.assets_path / template_name
        return template_path.exists()

    def get_template_path(self, template_name: str) -> Path:
        """Get full path to a template file.

        Args:
            template_name: Name of template file

        Returns:
            Full path to template

        Examples:
            >>> service = TemplateService()
            >>> path = service.get_template_path("main.py.j2")
        """
        return self.assets_path / template_name

    def list_templates(self, pattern: str = "*") -> list[str]:
        """List available templates matching pattern.

        Args:
            pattern: Glob pattern to match (default: all files)

        Returns:
            List of template names

        Examples:
            >>> service = TemplateService()
            >>> templates = service.list_templates("*.j2")
            >>> python_templates = service.list_templates("**/*.py")
        """
        templates = []
        for path in self.assets_path.rglob(pattern):
            if path.is_file():
                # Get relative path from assets folder
                rel_path = path.relative_to(self.assets_path)
                templates.append(str(rel_path))

        logger.debug(f"Found {len(templates)} templates matching '{pattern}'")
        return sorted(templates)

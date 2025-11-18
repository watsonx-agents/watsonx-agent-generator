"""Custom exceptions for WatsonX Agent Creator.

This module provides a hierarchy of custom exceptions for better error handling
and reporting throughout the application.
"""

from typing import Any


class AgentCreatorError(Exception):
    """Base exception for all WatsonX Agent Creator errors.

    This is the root exception class from which all other custom exceptions inherit.
    Catching this exception will catch all custom errors raised by the application.

    Attributes:
        message: Human-readable error message
        details: Optional dictionary containing additional error context
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception.

        Returns:
            Formatted error message with details if available
        """
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ValidationError(AgentCreatorError):
    """Exception raised when input validation fails.

    This exception is raised when user input or configuration fails validation checks.

    Examples:
        >>> raise ValidationError("Invalid agent name", {"name": "my-agent", "reason": "contains hyphens"})
    """


class ConfigurationError(AgentCreatorError):
    """Exception raised when configuration is invalid or missing.

    This exception is raised when there are issues with application configuration,
    such as missing environment variables or invalid settings.

    Examples:
        >>> raise ConfigurationError("Missing API key", {"env_var": "WATSONX_APIKEY"})
    """


class GenerationError(AgentCreatorError):
    """Exception raised when agent generation fails.

    This exception is raised when there are errors during the agent project
    generation process, such as template rendering failures or file I/O errors.

    Examples:
        >>> raise GenerationError("Template not found", {"template": "main.py.jinja2"})
    """


class AIServiceError(AgentCreatorError):
    """Exception raised when AI service interactions fail.

    This exception is raised when there are errors communicating with the
    WatsonX AI service or when AI-powered generation fails.

    Examples:
        >>> raise AIServiceError("API request failed", {"status_code": 500})
    """


class TemplateError(AgentCreatorError):
    """Exception raised when template processing fails.

    This exception is raised when there are errors loading or rendering
    Jinja2 templates.

    Examples:
        >>> raise TemplateError("Template syntax error", {"template": "dockerfile.j2"})
    """


class FileOperationError(AgentCreatorError):
    """Exception raised when file operations fail.

    This exception is raised when there are errors during file system operations
    such as reading, writing, copying, or deleting files.

    Examples:
        >>> raise FileOperationError("Failed to create directory", {"path": "/tmp/agent"})
    """

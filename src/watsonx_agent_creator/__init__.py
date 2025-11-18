"""WatsonX Agent Creator - Lightning-fast AI agent scaffolding for IBM watsonx.ai.

This package provides a beautiful CLI tool to generate production-ready AI agent projects
with support for multiple frameworks including WatsonX SDK, LangGraph, CrewAI, and more.

Author: Ruslan Magana
Website: https://ruslanmv.com
License: Apache-2.0
"""

__version__ = "2.0.0"
__author__ = "Ruslan Magana"
__email__ = "contact@ruslanmv.com"
__license__ = "Apache-2.0"

from watsonx_agent_creator.core.config import Settings
from watsonx_agent_creator.core.exceptions import (
    AgentCreatorError,
    ConfigurationError,
    GenerationError,
    ValidationError,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "Settings",
    "AgentCreatorError",
    "ConfigurationError",
    "GenerationError",
    "ValidationError",
]

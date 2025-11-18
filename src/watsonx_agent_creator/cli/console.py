"""Rich console configuration for beautiful terminal output.

This module provides a centralized Rich console instance with custom
themes and formatting for the CLI.
"""

from rich.console import Console
from rich.theme import Theme

# Custom theme for WatsonX Agent Creator
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "prompt": "bold magenta",
        "highlight": "bold blue",
        "dim": "dim white",
    }
)

# Global console instance
console = Console(theme=custom_theme)

__all__ = ["console"]

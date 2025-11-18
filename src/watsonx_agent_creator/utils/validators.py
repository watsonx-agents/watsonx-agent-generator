"""Input validation utilities.

This module provides validation functions for user input with clear
error messages and consistent validation logic.
"""

import re
from pathlib import Path

from watsonx_agent_creator.core.exceptions import ValidationError


def validate_agent_name(name: str) -> str:
    """Validate agent project name.

    Agent names must:
    - Be lowercase
    - Start with a letter
    - Contain only letters, numbers, and underscores
    - Be between 3 and 50 characters
    - Not start or end with underscore
    - Not contain consecutive underscores

    Args:
        name: Agent name to validate

    Returns:
        Validated agent name

    Raises:
        ValidationError: If name is invalid

    Examples:
        >>> validate_agent_name("my_agent")
        'my_agent'
        >>> validate_agent_name("MyAgent")  # raises ValidationError
        >>> validate_agent_name("_agent")  # raises ValidationError
    """
    if not name:
        raise ValidationError("Agent name cannot be empty")

    if len(name) < 3:
        raise ValidationError("Agent name must be at least 3 characters", {"name": name})

    if len(name) > 50:
        raise ValidationError("Agent name must be at most 50 characters", {"name": name})

    if not name.islower():
        raise ValidationError("Agent name must be lowercase", {"name": name})

    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        raise ValidationError(
            "Agent name must start with a letter and contain only lowercase letters, "
            "numbers, and underscores",
            {"name": name},
        )

    if name.startswith("_") or name.endswith("_"):
        raise ValidationError(
            "Agent name cannot start or end with underscore",
            {"name": name},
        )

    if "__" in name:
        raise ValidationError(
            "Agent name cannot contain consecutive underscores",
            {"name": name},
        )

    return name


def validate_email(email: str) -> str:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Validated email address

    Raises:
        ValidationError: If email is invalid

    Examples:
        >>> validate_email("user@example.com")
        'user@example.com'
        >>> validate_email("invalid")  # raises ValidationError
    """
    if not email:
        raise ValidationError("Email cannot be empty")

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", {"email": email})

    return email


def validate_port(port: int | str) -> int:
    """Validate port number.

    Args:
        port: Port number to validate (int or string)

    Returns:
        Validated port number

    Raises:
        ValidationError: If port is invalid

    Examples:
        >>> validate_port(8000)
        8000
        >>> validate_port("8080")
        8080
        >>> validate_port(80)  # raises ValidationError (too low)
        >>> validate_port(70000)  # raises ValidationError (too high)
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError) as e:
        raise ValidationError("Port must be a valid integer", {"port": port}) from e

    if port_int < 1000:
        raise ValidationError(
            "Port must be at least 1000 (ports below 1000 are privileged)",
            {"port": port_int},
        )

    if port_int > 65535:
        raise ValidationError(
            "Port must be at most 65535",
            {"port": port_int},
        )

    return port_int


def validate_path(path: str | Path, must_exist: bool = False) -> Path:
    """Validate file system path.

    Args:
        path: Path to validate
        must_exist: Whether path must already exist

    Returns:
        Validated Path object

    Raises:
        ValidationError: If path is invalid

    Examples:
        >>> validate_path("/tmp/output")
        PosixPath('/tmp/output')
        >>> validate_path("/tmp/output", must_exist=True)  # raises if doesn't exist
    """
    if isinstance(path, str):
        path = Path(path)

    # Resolve path
    try:
        resolved_path = path.expanduser().resolve()
    except (RuntimeError, OSError) as e:
        raise ValidationError("Invalid path", {"path": str(path), "error": str(e)}) from e

    if must_exist and not resolved_path.exists():
        raise ValidationError("Path does not exist", {"path": str(resolved_path)})

    return resolved_path


def validate_version(version: str) -> str:
    """Validate semantic version string.

    Args:
        version: Version string to validate (e.g., "1.0.0")

    Returns:
        Validated version string

    Raises:
        ValidationError: If version format is invalid

    Examples:
        >>> validate_version("1.0.0")
        '1.0.0'
        >>> validate_version("2.1.3")
        '2.1.3'
        >>> validate_version("1.0")  # raises ValidationError
    """
    pattern = r"^\d+\.\d+\.\d+$"

    if not re.match(pattern, version):
        raise ValidationError(
            "Version must follow semantic versioning (e.g., 1.0.0)",
            {"version": version},
        )

    return version

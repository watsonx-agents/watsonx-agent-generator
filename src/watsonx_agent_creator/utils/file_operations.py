"""Async file operation utilities.

This module provides async wrappers for common file operations with
proper error handling and logging.
"""

import shutil
from pathlib import Path
from typing import Any

import aiofiles
import toml

from watsonx_agent_creator.core.exceptions import FileOperationError
from watsonx_agent_creator.core.logging import get_logger

logger = get_logger(__name__)


async def read_file(file_path: Path) -> str:
    """Read file contents asynchronously.

    Args:
        file_path: Path to file to read

    Returns:
        File contents as string

    Raises:
        FileOperationError: If file cannot be read

    Examples:
        >>> content = await read_file(Path("example.txt"))
    """
    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
        logger.debug(f"Read file: {file_path}")
        return content
    except OSError as e:
        logger.error(f"Failed to read file: {file_path}", exc_info=True)
        raise FileOperationError(
            f"Failed to read file: {file_path}",
            {"path": str(file_path), "error": str(e)},
        ) from e


async def write_file(file_path: Path, content: str) -> None:
    """Write content to file asynchronously.

    Creates parent directories if they don't exist.

    Args:
        file_path: Path to file to write
        content: Content to write

    Raises:
        FileOperationError: If file cannot be written

    Examples:
        >>> await write_file(Path("output.txt"), "Hello, World!")
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)
        logger.debug(f"Wrote file: {file_path}")
    except OSError as e:
        logger.error(f"Failed to write file: {file_path}", exc_info=True)
        raise FileOperationError(
            f"Failed to write file: {file_path}",
            {"path": str(file_path), "error": str(e)},
        ) from e


def copy_file(src: Path, dst: Path) -> None:
    """Copy file from source to destination.

    Args:
        src: Source file path
        dst: Destination file path

    Raises:
        FileOperationError: If file cannot be copied

    Examples:
        >>> copy_file(Path("source.txt"), Path("dest.txt"))
    """
    try:
        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)
        logger.debug(f"Copied file: {src} -> {dst}")
    except (OSError, shutil.Error) as e:
        logger.error(f"Failed to copy file: {src} -> {dst}", exc_info=True)
        raise FileOperationError(
            f"Failed to copy file: {src} -> {dst}",
            {"src": str(src), "dst": str(dst), "error": str(e)},
        ) from e


def copy_directory(src: Path, dst: Path, ignore_patterns: list[str] | None = None) -> None:
    """Copy directory tree from source to destination.

    Args:
        src: Source directory path
        dst: Destination directory path
        ignore_patterns: List of patterns to ignore (e.g., ["*.pyc", "__pycache__"])

    Raises:
        FileOperationError: If directory cannot be copied

    Examples:
        >>> copy_directory(Path("src"), Path("dest"), ignore_patterns=["*.pyc"])
    """
    try:
        if ignore_patterns:
            ignore_func = shutil.ignore_patterns(*ignore_patterns)
        else:
            ignore_func = None

        shutil.copytree(src, dst, ignore=ignore_func, dirs_exist_ok=True)
        logger.debug(f"Copied directory: {src} -> {dst}")
    except (OSError, shutil.Error) as e:
        logger.error(f"Failed to copy directory: {src} -> {dst}", exc_info=True)
        raise FileOperationError(
            f"Failed to copy directory: {src} -> {dst}",
            {"src": str(src), "dst": str(dst), "error": str(e)},
        ) from e


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        Path object for the directory

    Raises:
        FileOperationError: If directory cannot be created

    Examples:
        >>> ensure_directory(Path("/tmp/my_dir"))
        PosixPath('/tmp/my_dir')
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")
        return path
    except OSError as e:
        logger.error(f"Failed to create directory: {path}", exc_info=True)
        raise FileOperationError(
            f"Failed to create directory: {path}",
            {"path": str(path), "error": str(e)},
        ) from e


def read_toml(file_path: Path) -> dict[str, Any]:
    """Read TOML file synchronously.

    Args:
        file_path: Path to TOML file

    Returns:
        Parsed TOML data as dictionary

    Raises:
        FileOperationError: If TOML cannot be read or parsed

    Examples:
        >>> data = read_toml(Path("config.toml"))
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            data = toml.load(f)
        logger.debug(f"Read TOML file: {file_path}")
        return data
    except (OSError, toml.TomlDecodeError) as e:
        logger.error(f"Failed to read TOML file: {file_path}", exc_info=True)
        raise FileOperationError(
            f"Failed to read TOML file: {file_path}",
            {"path": str(file_path), "error": str(e)},
        ) from e


def write_toml(file_path: Path, data: dict[str, Any]) -> None:
    """Write data to TOML file synchronously.

    Args:
        file_path: Path to TOML file
        data: Data to write

    Raises:
        FileOperationError: If TOML cannot be written

    Examples:
        >>> write_toml(Path("config.toml"), {"key": "value"})
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
        logger.debug(f"Wrote TOML file: {file_path}")
    except (OSError, TypeError) as e:
        logger.error(f"Failed to write TOML file: {file_path}", exc_info=True)
        raise FileOperationError(
            f"Failed to write TOML file: {file_path}",
            {"path": str(file_path), "error": str(e)},
        ) from e


def delete_path(path: Path, missing_ok: bool = True) -> None:
    """Delete file or directory.

    Args:
        path: Path to delete
        missing_ok: If True, don't raise error if path doesn't exist

    Raises:
        FileOperationError: If path cannot be deleted

    Examples:
        >>> delete_path(Path("/tmp/old_file.txt"))
        >>> delete_path(Path("/tmp/old_dir"), missing_ok=False)
    """
    try:
        if path.is_file():
            path.unlink(missing_ok=missing_ok)
        elif path.is_dir():
            shutil.rmtree(path, ignore_errors=missing_ok)
        elif not missing_ok:
            raise FileOperationError(
                f"Path does not exist: {path}",
                {"path": str(path)},
            )
        logger.debug(f"Deleted path: {path}")
    except OSError as e:
        logger.error(f"Failed to delete path: {path}", exc_info=True)
        raise FileOperationError(
            f"Failed to delete path: {path}",
            {"path": str(path), "error": str(e)},
        ) from e

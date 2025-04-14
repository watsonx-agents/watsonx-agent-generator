import re
import shlex
import subprocess
from pathlib import Path

from agent_creator.configs import Logger

app_logger = Logger("application").logger


def copy_and_substitute(from_path: Path | str, to_path: Path | str | None = None, **kwargs) -> None:
    to_path = to_path if to_path else from_path
    with open(from_path, "r", encoding="utf-8") as f:
        content: str = f.read()

    for key, value in kwargs.items():
        pattern = r"\{" + re.escape(key) + r"\}"
        content = re.sub(pattern, str(value), content)

    with open(to_path, "w", encoding="utf-8") as f:
        f.write(content)


def execute_command(command: str, cwd: str | Path | None = None) -> str:
    try:
        app_logger.debug(f"Executing command `{command}`...")
        result: subprocess.CompletedProcess[str] = subprocess.run(
            shlex.split(command), check=True, capture_output=True, text=True, cwd=cwd
        )
        app_logger.debug("Success!")
        if result.stdout.strip():
            app_logger.debug(f"Output:\n{result.stdout.strip()}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        app_logger.error(f"Error!")
        app_logger.error(f"Output:\n{e.stderr.strip()}")
        return ""


def is_snake_case(value: str) -> bool:
    # Type check: Ensure the input is a string
    if not isinstance(value, str):
        raise TypeError("Input must be a string")

    # Define the regex pattern for snake_case
    snake_case_pattern = r"^[a-z]+(_[a-z]+)*$"

    # Match the input against the pattern
    return bool(re.match(snake_case_pattern, value))

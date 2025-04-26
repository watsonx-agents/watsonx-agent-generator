## `agent_creator/parameters.py`
# -*- coding: utf-8 -*-
"""
agent_creator.parameters
~~~~~~~~~~~~~~~~~~~~~~~~

Interactive / CLI argument parsing for create-agent workflow.
"""

import argparse
from pathlib import Path
from subprocess import run, PIPE

from agent_creator.configs import DEFAULT_AGENT_BASE_PATH, Logger
from agent_creator.models import Arguments
from agent_creator.utils import is_snake_case

app_logger = Logger().logger


# --------------------------------------------------------------------------- #
# 1 · Git helpers
# --------------------------------------------------------------------------- #
def _git_config(name: str) -> str:
    """Return `git config --get <name>` or an empty string if unset/errored."""
    result = run(["git", "config", "--get", name],
                 stdout=PIPE, stderr=PIPE, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def get_git_info() -> tuple[str, str]:
    """(user.name, user.email) from Git or ("", "") if unavailable."""
    return _git_config("user.name"), _git_config("user.email")


# --------------------------------------------------------------------------- #
# 2 · Generic input helper
# --------------------------------------------------------------------------- #
def get_user_input(prompt: str, default: str | None = None) -> str:
    suffix = f" (default: {default})" if default else ""
    value  = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


# --------------------------------------------------------------------------- #
# 3 · Main parser
# --------------------------------------------------------------------------- #
def parse_arguments() -> Arguments:
    parser = argparse.ArgumentParser(description="Create and configure an agent")

    parser.add_argument("--agent-name",  type=str)
    parser.add_argument("--agent-path",  type=str,
                        help=f"Destination folder (default: {DEFAULT_AGENT_BASE_PATH})")
    parser.add_argument("--agent-port",  type=int)
    parser.add_argument("--host-port",   type=int)
    parser.add_argument("--author-name", type=str)
    parser.add_argument("--author-email", type=str)

    args = parser.parse_args()

    # Always have usable defaults for git_* variables
    try:
        git_name, git_email = get_git_info()
    except Exception:  # pragma: no cover
        git_name = git_email = ""

    # ------------------- agent_name (snake_case) --------------------------
    while True:
        agent_name = args.agent_name or get_user_input("Enter agent name (snake_case)")
        if is_snake_case(agent_name):
            break
        app_logger.warning("Name must be snake_case!")

    # ------------------- agent_path (directory) --------------------------
    while True:
        default_path = str(DEFAULT_AGENT_BASE_PATH)
        path_str = args.agent_path or get_user_input("Enter agent path", default_path)
        path = Path(path_str).expanduser().resolve()

        if not path.exists():
            if get_user_input(f"Path '{path}' does not exist. Create it? [y/N]", "n").lower() in ("y", "yes"):
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    app_logger.info(f"Directory '{path}' created.")
                    break
                except OSError as exc:  # pragma: no cover
                    app_logger.error(f"Failed to create path: {exc}")
            app_logger.warning("Please enter a valid path.")
        elif not path.is_dir():
            app_logger.warning("Path exists but is not a directory.")
        else:
            break

    agent_path = str(path)

    # ------------------- ports -------------------------------------------
    def _ask_port(label: str, provided: int | None) -> int:
        while True:
            port = provided or int(get_user_input(label))
            if 1000 <= port <= 9999:
                return port
            app_logger.warning("Port must be in the range [1000–9999].")

    agent_port = _ask_port("Enter agent port (1000-9999)", args.agent_port)
    host_port  = _ask_port("Enter host port  (1000-9999)", args.host_port or agent_port)

    # ------------------- author info -------------------------------------
    author_name  = args.author_name  or get_user_input("Author name",  git_name)
    author_email = args.author_email or get_user_input("Author email", git_email)

    # ------------------- return model ------------------------------------
    result = Arguments(
        agent_name   = agent_name,
        agent_path   = agent_path,
        agent_port   = agent_port,
        host_port    = host_port,
        author_name  = author_name,
        author_email = author_email,
    )
    app_logger.debug("Parsed arguments: %s", result)
    return result


# --------------------------------------------------------------------------- #
# 4 · CLI test
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    print(parse_arguments())

import argparse
import os

from agent_creator.configs import DEFAULT_AGENT_BASE_PATH, Logger
from agent_creator.models import Arguments
from agent_creator.utils import execute_command, is_snake_case
import os
from pathlib import Path
app_logger = Logger().logger


def get_git_info() -> tuple[str, str]:
    name: str = execute_command("git config user.name").strip()
    email: str = execute_command("git config user.email").strip()
    return name, email


def get_user_input(prompt: str, default_value: str | None = None) -> str:
    """Helper function to get input from the user with an optional default."""
    default_str: str = f" (default: {default_value})" if default_value else ""
    user_input = input(f"{prompt}{default_str}: ")
    if default_value or user_input:
        return user_input if user_input else str(default_value)
    else:
        app_logger.info("Mandatory parameter. You can't leave it blank!")
        return get_user_input(prompt, default_value)


def create_agent(agent_name: str, agent_path: str, agent_port: int, host_port: int) -> None:
    """Function that handles the logic for creating an agent."""
    # Example implementation (replace with actual agent creation logic)
    print(f"Creating agent '{agent_name}'")
    print(f"Agent path: {agent_path}")
    print(f"Exposing agent on port {agent_port} and binding to host port {host_port}")


def parse_arguments() -> Arguments:
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Create and configure an agent.")

    parser.add_argument("--agent-name", type=str, help="The name of the agent to be created.")

    parser.add_argument(
        "--agent-path",
        type=str,
        # default=DEFAULT_AGENT_BASE_PATH,
        help=f"The path where to store the agent (default: {DEFAULT_AGENT_BASE_PATH}).",
    )

    parser.add_argument("--agent-port", type=int, help="The port to expose the agent.")

    parser.add_argument(
        "--host-port",
        type=int,
        help="The port to bind the container's port (default: same as agent port).",
    )

    parser.add_argument("--author-name", type=str, help="The name and surname of the author creating the agent")

    parser.add_argument("--author-email", type=str, help="The email of the author creating the agent")

    # Parse arguments
    args = parser.parse_args()

    git_name, git_email = get_git_info()

    # Ask for missing arguments interactively if they are not provided
    name_snake_case = False
    while not name_snake_case:
        agent_name: str = args.agent_name or get_user_input("Enter agent name (snake_case)").strip()
        name_snake_case = is_snake_case(agent_name)
        if not name_snake_case:
            app_logger.warning("The name should be snake_case!")

    is_valid_path = False
  #  while not is_valid_path:
  #      agent_path: str = args.agent_path or get_user_input(f"Enter agent path", str(DEFAULT_AGENT_BASE_PATH)).strip()
  #      is_valid_path = os.path.exists(agent_path)
  #      if not is_valid_path:
  #          app_logger.warning("The path must be valid!")

    while not is_valid_path:
        agent_path_str: str = args.agent_path or get_user_input(f"Enter agent path", str(DEFAULT_AGENT_BASE_PATH)).strip()
        agent_path_obj = Path(agent_path_str).expanduser().resolve()
        if not agent_path_obj.exists():
            create = input(f"Path '{agent_path_obj}' does not exist. Do you want to create it? [y/N]: ").strip().lower()
            if create in ["y", "yes"]:
                try:
                    agent_path_obj.mkdir(parents=True, exist_ok=True)
                    print(f"Directory '{agent_path_obj}' created.")
                    is_valid_path = True
                    agent_path = str(agent_path_obj) # Update agent_path
                except OSError as e:
                    app_logger.error(f"Error creating directory '{agent_path_obj}': {e}")
                    app_logger.warning("Failed to create the path. Please enter a valid path.")
            else:
                app_logger.warning("The path must be valid!")
        elif not agent_path_obj.is_dir():
            app_logger.warning(f"Error: '{agent_path_obj}' is not a directory. Please enter a valid path.")
            is_valid_path = False
        else:
            is_valid_path = True
            agent_path = str(agent_path_obj) # Update agent_path




    is_port_valid = False
    while not is_port_valid:
        agent_port: int = args.agent_port or int(get_user_input("Enter agent port (1000-9999)"))
        is_port_valid = 1000 <= agent_port <= 9999
        if not is_port_valid:
            app_logger.warning("The port should be in the range [1000-9999]!")

    is_port_valid = False
    while not is_port_valid:
        host_port: int = args.host_port or int(get_user_input("Enter host port (1000-9999)", str(agent_port)))
        is_port_valid = 1000 <= host_port <= 9999
        if not is_port_valid:
            app_logger.warning("The port should be in the range [1000-9999]!")

    author_name: str = args.author_name or get_user_input("Author name", git_name).strip()
    author_email: str = args.author_email or get_user_input("Author email", git_email).strip()

    # Call the function that creates the agent
    result: Arguments = Arguments(
        agent_name=agent_name,
        agent_path=agent_path,
        agent_port=agent_port,
        host_port=host_port,
        author_name=author_name,
        author_email=author_email,
    )
    app_logger.debug(f"Parsed arguments {result}")
    return result


if __name__ == "__main__":
    print(parse_arguments())

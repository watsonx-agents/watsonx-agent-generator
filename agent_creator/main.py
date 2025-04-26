import os
import shutil
from pathlib import Path
from traceback import format_exc

from agent_creator.configs import ASSETS_FOLDER, Logger
from agent_creator.models import (
    Arguments,
    Compose,
    Configs,
    Dockerfile,
    Env,
    Poetry,
    ProjectFile,
    Readme,
)
from agent_creator.parameters import parse_arguments
from agent_creator.utils import copy_and_substitute, execute_command

import subprocess  # For running git config commands
import toml
import requests
import json
from dotenv import load_dotenv

# Import the generate_agent function from the generator module
from agent_creator.generator import generate_agent

app_logger = Logger("application").logger
dependencies: list[str] = [
    "isort",
    "black",
    "langchain",
    "langgraph",
    "python-dotenv",
    "fastapi",
    "uvicorn",
    "pydantic",
    "python-dateutil",
]

# -----------------------------------------------------------------------------
# New Framework Selection and Customization Functions
# -----------------------------------------------------------------------------
def select_framework():
    options = [
        'watsonx sdk',
        'beeai',
        'langraph',
        'crewai',
        'langflow',
        'no framework'
    ]
    
    print("Select a framework from the following options:")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
        
    choice = input("Enter the number corresponding to your choice: ")
    
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(options):
            raise ValueError
        return options[index]
    except ValueError:
        print("Invalid input. Please run the script again and provide a valid number.")
        exit(1)

def setup_framework(selected_framework):
    # The base directory for the frameworks is inside assets/frameworks
    project_root = os.getcwd()
    frameworks_dir = os.path.join(project_root, 'assets', 'frameworks')
    os.makedirs(frameworks_dir, exist_ok=True)
    
    # Define the source model folder (assumed to be assets/model)
    source_model_path = os.path.join(project_root, 'assets', 'model')
    if not os.path.exists(source_model_path):
        print(f"Source model folder does not exist at {source_model_path}.")
        exit(1)
    
    # Normalize destination folder name: "no framework" becomes "base"
    if selected_framework.lower() == "no framework":
        dest_folder = "base"
    else:
        dest_folder = selected_framework.split()[0].lower()
    
    # Destination directory: assets/frameworks/<dest_folder>/model
    destination_model_dir = os.path.join(frameworks_dir, dest_folder, 'model')
    os.makedirs(destination_model_dir, exist_ok=True)
    
    # Copy each file from the original model directory to the destination directory
    for item in os.listdir(source_model_path):
        s = os.path.join(source_model_path, item)
        d = os.path.join(destination_model_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    
    print(f"Model files have been copied to {destination_model_dir}.")

def customize_model(selected_framework):
    """
    Prompt the user for a new task description to update the agent code
    using generator.py. The updated code is written to agent_custom.py.
    """
    answer = input("Would you like to customize the model? [Y/n]: ").strip().lower()
    if answer in ["", "y", "yes"]:
        # Determine the framework destination folder (use same normalization as in setup_framework)
        if selected_framework.lower() == "no framework":
            dest_folder = "base"
        else:
            dest_folder = selected_framework.split()[0].lower()
        
        # Load the respective agent.py code from assets/frameworks/<dest_folder>/model
        framework_agent_path = os.path.join(
            os.getcwd(),
            "assets", "frameworks", dest_folder, "model", "agent.py"
        )
        if not os.path.exists(framework_agent_path):
            print(f"Agent file not found at {framework_agent_path}!")
            return
        
        with open(framework_agent_path, "r", encoding="utf-8") as f:
            framework_agent_code = f.read()
        
        # Ask the user for the new task description for the agent
        prompt_text = (
            f"You have selected the framework '{selected_framework}'.\n"
            "Please provide the new task description for the agent (currently supports single agents): "
        )
        task_description = input(prompt_text)
        
        # Generate the updated code using generator.py's generate_agent function
        updated_code = generate_agent(framework_agent_code, task_description)
        if not updated_code:
            print("Agent code generation failed.")
            return
        
        # Write the updated code to agent_custom.py in the project root
        custom_agent_path = os.path.join(os.getcwd(), "agent_custom.py")
        with open(custom_agent_path, "w", encoding="utf-8") as f:
            f.write(updated_code)
        
        print(f"Customized agent code has been created at: {custom_agent_path}")
    else:
        print("Model customization skipped.")

# -----------------------------------------------------------------------------
# Existing Functions for Creating Project Files
# -----------------------------------------------------------------------------
def create_dockerfile(dockerfile: Dockerfile) -> None:
    app_logger.info(f"Creating Dockerfile in `{dockerfile.to_path}`")
    copy_and_substitute(dockerfile.from_path, dockerfile.to_path, AGENT_NAME=dockerfile.agent_name)

def create_compose(compose: Compose) -> None:
    app_logger.info(f"Creating compose in `{compose.to_path}`")
    copy_and_substitute(
        compose.from_path,
        compose.to_path,
        HOST_PORT=compose.host_port,
        AGENT_PORT=compose.agent_port,
        AGENT_NAME=compose.agent_name,
    )

def create_readme(readme: Readme) -> None:
    app_logger.info(f"Creating README.md in `{readme.to_path}`")
    agent_name = " ".join(s.capitalize() for s in readme.agent_name.split("_"))
    copy_and_substitute(
        readme.from_path,
        readme.to_path,
        AGENT_NAME=agent_name,
        AGENT_PATH=readme.agent_path,
        HOST_PORT=readme.host_port,
    )

    # Set author name to default "IBM Platform" and use email if provided
    author_name = "IBM Platform"
    author_email = readme.author_email or ""

    # Build the author content
    author_content = f"\n## Author\n\n- {author_name}"
    if author_email:
        author_content += f" <[{author_email}](mailto:{author_email})>"

    with open(readme.to_path, "a", encoding="utf-8") as f:
        f.write(author_content)

def create_gitignore(file: ProjectFile) -> None:
    app_logger.info(f"Creating .gitignore in `{file.to_path}`")
    shutil.copy2(file.from_path, file.to_path)

def create_env(env: Env) -> None:
    app_logger.info(f"Creating .env in `{env.to_path}`")
    copy_and_substitute(env.from_path, env.to_path, AGENT_PORT=env.agent_port)
    shutil.copy2(env.to_path, str(env.to_path).replace(".sample", ""))

def create_poetry(poetry: Poetry) -> None:
    app_logger.info(f"Creating poetry project in `{poetry.base_path}`")

    # Step 1: Create project using poetry new
    project_path = Path(poetry.base_path) / poetry.agent_name
    execute_command(f"poetry new {project_path}", cwd=poetry.base_path)

    # Step 2: Add dependencies
    app_logger.info("Adding dependencies")
    execute_command(
        f"poetry add {' '.join(dependencies)}",
        cwd=project_path,
    )

    # Step 3: Update pyproject.toml with the correct author information
    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists():
        pyproject_content = toml.load(pyproject_file)

        # Add author information
        author_info = f"{poetry.author_name} <{poetry.author_email}>" if poetry.author_email else poetry.author_name
        pyproject_content['tool']['poetry']['authors'] = [author_info]

        # Write the updated configuration back to pyproject.toml
        with open(pyproject_file, "w") as f:
            toml.dump(pyproject_content, f)

        app_logger.info("Updated pyproject.toml with correct author information.")
    else:
        app_logger.error("pyproject.toml not found.")

def create_configs_folder(configs: Configs) -> None:
    app_logger.info(f"Copying configs from `{configs.from_path}` to `{configs.to_path}`")
    shutil.copytree(configs.from_path, configs.to_path)
    copy_and_substitute(configs.to_path / "logger.py", None, AGENT_NAME=configs.agent_name)

def create_model_folder(configs: Configs) -> None:
    app_logger.info(f"Copying model folder from `{configs.from_path}` to `{configs.to_path}`")
    shutil.copytree(configs.from_path, configs.to_path)

def create_main_file(configs: Configs) -> None:
    app_logger.info(f"Copying main file from `{configs.from_path}` to `{configs.to_path}`")
    copy_and_substitute(configs.from_path, configs.to_path, AGENT_NAME=configs.agent_name)



def update_agents_json(agent_name: str, agent_port: int, agent_description: str, base_path: Path) -> None:
    """
    Append the new agent details to agents.json. If the file doesn't exist, create it.
    """
    agents_file = base_path / "agents.json"
    agent_data = {
        "name": agent_name,
        "description": agent_description,
        "port": agent_port,
        "host": "localhost",
        "repo": f"https://github.com/watsonx-agents/agent_{agent_name}",
        "status": "stopped",
        "pid": None
    }

    # Load existing data or initialize new structure
    if agents_file.exists():
        with open(agents_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {"agents": []}

    # Append the new agent data
    data["agents"].append(agent_data)

    # Write the updated data back to the JSON file
    with open(agents_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    app_logger.info(f"Agent '{agent_name}' added to agents.json")

def create_project(arguments: Arguments) -> None:
    # Ensure the base agent path is valid. If not, create it.
    base_path = Path(arguments.agent_path).resolve()
    if not base_path.exists():
        app_logger.info(f"The path {base_path} does not exist. Creating it...")
        base_path.mkdir(parents=True, exist_ok=True)

    agent_folder = base_path / arguments.agent_name
    agent_poetry_folder = agent_folder / arguments.agent_name
    agent_poetry_real_folder = agent_folder / "app"

    from_dockerfile: Path = ASSETS_FOLDER / "Dockerfile"
    to_dockerfile: Path = agent_folder / "Dockerfile"

    from_compose: Path = ASSETS_FOLDER / "compose.yaml"
    to_compose: Path = agent_folder / "compose.yaml"

    from_readme: Path = ASSETS_FOLDER / "README.md"
    to_readme: Path = agent_folder / "README.md"

    from_gitignore: Path = ASSETS_FOLDER / ".gitignore"
    to_gitignore: Path = agent_folder / ".gitignore"

    from_env: Path = ASSETS_FOLDER / ".env.sample"
    to_env: Path = agent_folder / ".env.sample"

    from_configs = ASSETS_FOLDER / "configs"
    to_configs = agent_poetry_real_folder / arguments.agent_name / "configs"

    from_model = ASSETS_FOLDER / "model"
    to_model = agent_poetry_real_folder / arguments.agent_name / "model"

    from_main = ASSETS_FOLDER / "main.py"
    to_main = agent_poetry_real_folder / arguments.agent_name / "main.py"

    # check if overwrite is needed
    overwrite: bool = False
    if os.path.exists(agent_folder):
        overwrite = input(f"Overwrite the content of {agent_folder}? [y/N] ").lower() in [
            "t",
            "true",
            "1",
            "y",
            "yes",
            "",
        ]
        if overwrite:
            app_logger.info(f"Deleting {agent_folder}")
            shutil.rmtree(agent_folder)
    else:
        overwrite = True

    # Abort if user chooses not to overwrite
    if not overwrite:
        app_logger.info(f"Aborting. Not writing agent in {agent_folder}")
        return

    app_logger.info(f"Writing agent in {agent_folder}")
    os.makedirs(agent_folder, exist_ok=overwrite)
    create_dockerfile(Dockerfile(from_dockerfile, to_dockerfile, arguments.agent_name))
    create_compose(
        Compose(
            from_compose,
            to_compose,
            arguments.agent_name,
            arguments.host_port,
            arguments.agent_port,
        )
    )
    create_readme(
        Readme(
            from_readme,
            to_readme,
            agent_name=arguments.agent_name,
            agent_path=str(agent_folder),
            host_port=arguments.host_port,
            author_name=arguments.author_name,
            author_email=arguments.author_email,
        )
    )
    create_gitignore(ProjectFile(from_gitignore, to_gitignore))
    create_env(Env(from_env, to_env, arguments.agent_port))
    create_poetry(Poetry(base_path=agent_folder, agent_name=arguments.agent_name, author_name=arguments.author_name, author_email=arguments.author_email))
    agent_poetry_folder.rename(agent_poetry_real_folder)
    create_configs_folder(Configs(from_configs, to_configs, agent_name=arguments.agent_name))
    create_model_folder(Configs(from_model, to_model, agent_name=arguments.agent_name))
    create_main_file(Configs(from_main, to_main, agent_name=arguments.agent_name))
    app_logger.info("Formatting files...")
    execute_command(f"isort {agent_poetry_real_folder}")
    execute_command(f"black {agent_poetry_real_folder}")


def main():
    try:
        # -------------------------------------------------------------------------
        # New Step: Framework Selection, Setup, and Optional Model Customization
        # -------------------------------------------------------------------------
        framework = select_framework()
        setup_framework(framework)
        customize_model(framework)
        
        # Continue with parsing arguments and creating the project
        arguments: Arguments = parse_arguments()
        create_project(arguments)
        app_logger.info(f"Success! Agent {arguments.agent_name} created in {arguments.agent_path}")

 

    except KeyboardInterrupt:
        app_logger.info("\nExiting...")
    except Exception as e:
        app_logger.error("ERROR!")
        app_logger.error(format_exc())
    finally:
        app_logger.info("Bye bye! 👋😊")

if __name__ == "__main__":
    main()

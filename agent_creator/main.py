"""
agent_creator.main
~~~~~~~~~~~~~~~~~~

CLI entry-point for creating a new agent package.  Key updates:

* Agents now default to `./agents/` (not `../src/agents/`).
* Environment template falls back to `.env_template` if
  `assets/.env.sample` is missing.
* Watsonx-based code customisation is robust to SDK response types.
"""

import os
import shutil
from pathlib import Path
from traceback import format_exc

from agent_creator.configs import (
    ASSETS_FOLDER,
    Logger,
    DEFAULT_AGENT_BASE_PATH,
)
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

from agent_creator.generator import generate_agent

import sys
import tomlkit                    # add to your project if not already present

from agent_creator.configs import ASSETS_FOLDER, Logger
from agent_creator.utils import execute_command

app_logger = Logger("application").logger
app_logger = Logger("application").logger

def _folder_from_framework(name: str) -> str:
    """Convert user choice to folder slug used under assets/frameworks/."""
    return "base" if name.lower() == "no framework" else name.split()[0].lower()



# --------------------------------------------------------------------------- #
# Dependencies that are added to each generated Poetry project
# --------------------------------------------------------------------------- #
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

# --------------------------------------------------------------------------- #
# 1 · Framework selection & optional model customisation
# --------------------------------------------------------------------------- #
def select_framework() -> str:
    options = [
        "watsonx sdk",
        "beeai",
        "langraph",
        "crewai",
        "langflow",
        "no framework",
    ]
    print("Select a framework:")
    for idx, name in enumerate(options, 1):
        print(f"{idx}. {name}")

    try:
        idx = int(input("Enter the number corresponding to your choice: ")) - 1
        return options[idx]
    except Exception:  # pragma: no cover
        print("Invalid input — exiting.")
        exit(1)


def setup_framework(selected_framework: str) -> None:
    """Copy the baseline model template into assets/frameworks/<name>/model."""
    project_root = Path.cwd()
    frameworks_dir = project_root / "assets" / "frameworks"
    frameworks_dir.mkdir(parents=True, exist_ok=True)

    source_model_path = project_root / "assets" / "model"
    if not source_model_path.exists():  # pragma: no cover
        print(f"Cannot find template model in {source_model_path}")
        exit(1)

    dest_folder = (
        "base" if selected_framework.lower() == "no framework"
        else selected_framework.split()[0].lower()
    )
    destination_model_dir = frameworks_dir / dest_folder / "model"
    destination_model_dir.mkdir(parents=True, exist_ok=True)

    for item in source_model_path.iterdir():
        target = destination_model_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)

    print(f"Model files copied to {destination_model_dir}")


def customize_model(selected_framework: str) -> None:
    """Call Watsonx to patch the agent template for a new task."""
    ans = input("Would you like to customise the model? [Y/n]: ").strip().lower()
    if ans not in ("", "y", "yes"):
        print("Model customisation skipped.")
        return

    dest_folder = (
        "base" if selected_framework.lower() == "no framework"
        else selected_framework.split()[0].lower()
    )
    agent_path = (
        Path.cwd() / "assets" / "frameworks" / dest_folder / "model" / "agent.py"
    )
    if not agent_path.exists():  # pragma: no cover
        print(f"Cannot find {agent_path}")
        return

    current_code = agent_path.read_text(encoding="utf-8")
    task_description = input(
        f"You selected ‘{selected_framework}’\n"
        "Describe the new task the agent must perform: "
    )

    try:
        updated = generate_agent(current_code, task_description)
    except Exception as exc:  # pragma: no cover
        print(f"Customisation failed: {exc}")
        return

    if not updated:
        print("Agent code generation failed.")
        return

    (Path.cwd() / "agent_custom.py").write_text(updated, encoding="utf-8")
    print("Customised agent code written to ./agent_custom.py")

# --------------------------------------------------------------------------- #
# 2 · Helpers that actually write out project files
# --------------------------------------------------------------------------- #
def create_env(env: Env) -> None:
    """Create .env.sample + .env, falling back to .env_template if needed."""
    app_logger.info(f"Creating .env in {env.to_path}")
    sample = env.from_path
    if not sample.exists():
        fallback = Path(__file__).parent / ".env_template"
        if not fallback.exists():  # pragma: no cover
            raise FileNotFoundError("No .env sample or template available.")
        sample = fallback

    copy_and_substitute(sample, env.to_path, AGENT_PORT=env.agent_port)
    shutil.copy2(env.to_path, env.to_path.with_suffix(""))  # write plain .env


def create_dockerfile(dockerfile: Dockerfile) -> None:
    app_logger.info(f"Creating Dockerfile → {dockerfile.to_path}")
    copy_and_substitute(
        dockerfile.from_path, dockerfile.to_path, AGENT_NAME=dockerfile.agent_name
    )


def create_compose(compose: Compose) -> None:
    app_logger.info(f"Creating compose → {compose.to_path}")
    copy_and_substitute(
        compose.from_path,
        compose.to_path,
        HOST_PORT=compose.host_port,
        AGENT_PORT=compose.agent_port,
        AGENT_NAME=compose.agent_name,
    )


def create_readme(readme: Readme) -> None:
    app_logger.info(f"Creating README.md → {readme.to_path}")
    agent_title = " ".join(word.capitalize() for word in readme.agent_name.split("_"))
    copy_and_substitute(
        readme.from_path,
        readme.to_path,
        AGENT_NAME=agent_title,
        AGENT_PATH=readme.agent_path,
        HOST_PORT=readme.host_port,
    )
    footer = f"\n## Author\n\n- {readme.author_name}"
    if readme.author_email:
        footer += f" <{readme.author_email}>"
    with open(readme.to_path, "a", encoding="utf-8") as fh:
        fh.write(footer)


def create_gitignore(src: ProjectFile) -> None:
    app_logger.info(f"Creating .gitignore → {src.to_path}")
    shutil.copy2(src.from_path, src.to_path)


def create_poetry_old(poetry: Poetry) -> None:
    """Initialise a poetry project and inject dependencies + author."""
    app_logger.info(f"Initialising Poetry project in {poetry.base_path}")
    project_dir = Path(poetry.base_path) / poetry.agent_name
    execute_command(f"poetry new {project_dir}", cwd=poetry.base_path)
    execute_command(f"poetry add {' '.join(dependencies)}", cwd=project_dir)

    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        import toml

        data = toml.load(pyproject)
        author = (
            f"{poetry.author_name} <{poetry.author_email}>"
            if poetry.author_email
            else poetry.author_name
        )
        data["tool"]["poetry"]["authors"] = [author]
        pyproject.write_text(toml.dumps(data), encoding="utf-8")
        app_logger.info("Updated pyproject.toml author field.")
    else:  # pragma: no cover
        app_logger.error("pyproject.toml not found after ‘poetry new’!")


# --------------------------------------------------------------------------- #
def _caret_to_pep508(spec: str) -> str:
    """Convert ^X.Y.Z → >=X.Y.Z,<X+1.0.0 for PEP 508 lists."""
    if not spec.startswith("^"):
        return spec
    ver = spec[1:].strip()
    major = int(ver.split(".")[0])
    return f">={ver},<{major+1}.0.0"
# --------------------------------------------------------------------------- #

def create_poetry(poetry: Poetry, framework_folder: str | None = None) -> None:
    import sys, tomlkit

    project_dir = Path(poetry.base_path) / poetry.agent_name
    app_logger.info("Initialising Poetry project in %s", project_dir)

    # 1) Bootstrap
    execute_command(f"poetry new {project_dir}", cwd=poetry.base_path)
    pyproject = project_dir / "pyproject.toml"
    doc = tomlkit.parse(pyproject.read_text(encoding="utf-8"))

    # 2) Tables
    project_tbl = doc.setdefault("project", tomlkit.table())
    tool_tbl    = doc.setdefault("tool",    tomlkit.table())
    poetry_tbl  = tool_tbl.setdefault("poetry", tomlkit.table())

    proj_deps = project_tbl.setdefault("dependencies", tomlkit.array())
    po_deps   = poetry_tbl.setdefault("dependencies",  tomlkit.table())

    # 3) Python requirement
    if framework_folder == "watsonx":
        # Watsonx.ai only supports <3.13
        python_spec = ">=3.10,<3.13"
    else:
        host_py     = f"{sys.version_info.major}.{sys.version_info.minor}"
        python_spec = f">={host_py},<4.0"

    project_tbl["requires-python"] = python_spec
    po_deps["python"]              = python_spec

    # 4) Author
    author_it = tomlkit.inline_table()
    author_it["name"] = poetry.author_name
    if poetry.author_email:
        author_it["email"] = poetry.author_email
    project_tbl["authors"] = [author_it]
    poetry_tbl["authors"]  = [f"{poetry.author_name} <{poetry.author_email}>"]

    # 5) Merge framework fragment
    if framework_folder:
        frag_path = (
            ASSETS_FOLDER
            / "frameworks"
            / framework_folder
            / "pyproject.fragment.toml"
        )
        if frag_path.exists():
            frag_doc  = tomlkit.parse(frag_path.read_text(encoding="utf-8"))
            frag_deps = frag_doc["tool"]["poetry"].get("dependencies", {})

            # PEP 621: convert caret 
            for name, spec in frag_deps.items():
                if name == "python":
                    # already handled above
                    continue
                proj_deps.append(f"{name} {_caret_to_pep508(spec)}")

            # legacy: keep original caret
            po_deps.update(frag_deps)

            # copy additional [tool.*] sections (e.g. isort, black)
            for sect, val in frag_doc["tool"].items():
                if sect != "poetry":
                    tool_tbl[sect] = val

    # 6) Generic bundle (no langgraph here – it lives in its fragment)
    generic = [
        "isort",
        "black",
        "langchain",
        "python-dotenv",
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dateutil",
    ]
    existing = {dep.split()[0] for dep in proj_deps}
    for pkg in generic:
        if pkg not in existing:
            proj_deps.append(pkg)

    # 7) Write & lock
    pyproject.write_text(tomlkit.dumps(doc), encoding="utf-8")

    # `poetry lock` writes poetry.lock (no --no-update needed)
    execute_command("poetry lock", cwd=project_dir)
    app_logger.info("Poetry project ready (lock file generated).")



# --------------------------------------------------------------------------- #
def create_configs_folder(cfg: Configs) -> None:
    app_logger.info(f"Copying configs → {cfg.to_path}")
    shutil.copytree(cfg.from_path, cfg.to_path)
    copy_and_substitute(cfg.to_path / "logger.py", None, AGENT_NAME=cfg.agent_name)


def create_model_folder(cfg: Configs) -> None:
    app_logger.info(f"Copying model folder → {cfg.to_path}")
    shutil.copytree(cfg.from_path, cfg.to_path)


def create_main_file(cfg: Configs) -> None:
    app_logger.info(f"Copying main.py → {cfg.to_path}")
    copy_and_substitute(cfg.from_path, cfg.to_path, AGENT_NAME=cfg.agent_name)

# --------------------------------------------------------------------------- #
# 3 · JSON registry of all generated agents
# --------------------------------------------------------------------------- #
def update_agents_json(
    agent_name: str, agent_port: int, description: str, base_path: Path
) -> None:
    agents_file = base_path / "agents.json"
    record = {
        "name": agent_name,
        "description": description,
        "port": agent_port,
        "host": "localhost",
        "repo": f"https://github.com/watsonx-agents/agent_{agent_name}",
        "status": "stopped",
        "pid": None,
    }

    data = {"agents": []}
    if agents_file.exists():
        import json

        data = json.loads(agents_file.read_text(encoding="utf-8"))

    data["agents"].append(record)
    agents_file.write_text(
        __import__("json").dumps(data, indent=4), encoding="utf-8"
    )
    app_logger.info(f"Registered {agent_name} in agents.json")

# --------------------------------------------------------------------------- #
# 4 · Core project-creation routine
# --------------------------------------------------------------------------- #
def create_project(arguments: Arguments, framework_folder: str) -> None:
    # Use ./agents unless caller supplied a custom --agent-path
    if str(arguments.agent_path) == str(DEFAULT_AGENT_BASE_PATH):
        arguments.agent_path = str(Path.cwd() / "agents")

    base_path = Path(arguments.agent_path).expanduser().resolve()
    base_path.mkdir(parents=True, exist_ok=True)

    agent_folder = base_path / arguments.agent_name
    app_logger.info(f"Writing agent in {agent_folder}")

    # 4-A source ↦ target mappings
    agent_poetry_folder = agent_folder / arguments.agent_name      # tmp
    agent_poetry_real   = agent_folder / "app"                     # final

    paths = {
        "dockerfile": (ASSETS_FOLDER / "Dockerfile", agent_folder / "Dockerfile"),
        "compose":    (ASSETS_FOLDER / "compose.yaml", agent_folder / "compose.yaml"),
        "readme":     (ASSETS_FOLDER / "README.md",     agent_folder / "README.md"),
        "gitignore":  (ASSETS_FOLDER / ".gitignore",    agent_folder / ".gitignore"),
        "env":        (ASSETS_FOLDER / ".env.sample",   agent_folder / ".env.sample"),
        "configs":    (
            ASSETS_FOLDER / "configs",
            agent_poetry_real / arguments.agent_name / "configs",
        ),
        "model":      (
            ASSETS_FOLDER / "model",
            agent_poetry_real / arguments.agent_name / "model",
        ),
        "main":       (
            ASSETS_FOLDER / "main.py",
            agent_poetry_real / arguments.agent_name / "main.py",
        ),
    }

    # Overwrite guard
    if agent_folder.exists():
        confirm = input(f"{agent_folder} exists. Overwrite? [y/N]: ").lower()
        if confirm not in ("y", "yes"):
            app_logger.info("Aborting.")
            return
        shutil.rmtree(agent_folder)

    agent_folder.mkdir(parents=True, exist_ok=True)

    # 4-B create files
    create_dockerfile(Dockerfile(*paths["dockerfile"], arguments.agent_name))
    create_compose(
        Compose(
            *paths["compose"],
            agent_name=arguments.agent_name,
            host_port=arguments.host_port,
            agent_port=arguments.agent_port,
        )
    )
    create_readme(
        Readme(
            *paths["readme"],
            agent_name=arguments.agent_name,
            agent_path=str(agent_folder),
            host_port=arguments.host_port,
            author_name=arguments.author_name,
            author_email=arguments.author_email,
        )
    )
    create_gitignore(ProjectFile(*paths["gitignore"]))
    create_env(Env(*paths["env"], arguments.agent_port))
    create_poetry(
        Poetry(
            base_path=agent_folder,
            agent_name=arguments.agent_name,
            author_name=arguments.author_name,
            author_email=arguments.author_email,
        ),
        framework_folder=framework_folder,       # ← forward it!
    )

    # Poetry scaffold comes out in <agent_folder>/<agent_name>/… ;
    # rename it to <agent_folder>/app for cleaner docker image
    agent_poetry_folder.rename(agent_poetry_real)

    create_configs_folder(Configs(*paths["configs"], agent_name=arguments.agent_name))
    create_model_folder(Configs(*paths["model"],   agent_name=arguments.agent_name))
    create_main_file  (Configs(*paths["main"],    agent_name=arguments.agent_name))

    # Black / isort
    app_logger.info("Formatting generated code…")
    execute_command(f"isort {agent_poetry_real}")
    execute_command(f"black {agent_poetry_real}")

    # Finally add to agents.json
    update_agents_json(
        arguments.agent_name,
        arguments.agent_port,
        f"Agent generated from {arguments.agent_name}",
        base_path,
    )

# --------------------------------------------------------------------------- #
# 5 · CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    try:
        framework_ui = select_framework()
        framework_folder = _folder_from_framework(framework_ui)

        setup_framework(framework_ui)
        customize_model(framework_ui)

        args = parse_arguments()
        create_project(args, framework_folder)   # ← pass it!

        app_logger.info(
            f"✅ Success!  Agent “{args.agent_name}” created in {args.agent_path}"
        )
    except KeyboardInterrupt:
        app_logger.info("\nExiting…")
    except Exception:  # pragma: no cover
        app_logger.error("ERROR!")
        app_logger.error(format_exc())
    finally:
        app_logger.info("Bye bye! 👋😊")


if __name__ == "__main__":
    main()



# --------------------------------------------------------------------------- #

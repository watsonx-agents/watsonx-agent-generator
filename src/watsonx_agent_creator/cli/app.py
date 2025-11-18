"""Main CLI application using Typer and Rich.

This module provides the beautiful command-line interface for WatsonX Agent Creator
with interactive prompts, progress bars, and rich formatting.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from watsonx_agent_creator import __version__
from watsonx_agent_creator.cli.console import console
from watsonx_agent_creator.core.config import get_settings
from watsonx_agent_creator.core.exceptions import AgentCreatorError
from watsonx_agent_creator.core.logging import setup_logging
from watsonx_agent_creator.domain.models import (
    AIModelConfig,
    AgentConfig,
    DockerConfig,
    Framework,
    ProjectMetadata,
)
from watsonx_agent_creator.domain.schemas import FrameworkInfo
from watsonx_agent_creator.services.ai_service import AIService
from watsonx_agent_creator.services.generator import AgentGenerator
from watsonx_agent_creator.utils.validators import validate_agent_name, validate_email, validate_port

app = typer.Typer(
    name="watsonx-agent",
    help="⚡ Lightning-fast AI agent scaffolding for IBM watsonx.ai",
    add_completion=False,
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        console.print(
            Panel(
                f"[bold cyan]WatsonX Agent Creator[/] v{__version__}\n"
                f"[dim]Lightning-fast AI agent scaffolding for IBM watsonx.ai[/]\n\n"
                f"Author: Ruslan Magana\n"
                f"Website: https://ruslanmv.com\n"
                f"License: Apache-2.0",
                title="🚀 Version Info",
                border_style="cyan",
            )
        )
        raise typer.Exit()


@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """WatsonX Agent Creator CLI."""


@app.command(name="create")
def create_agent(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Agent project name"),
    framework: Optional[str] = typer.Option(None, "--framework", "-f", help="Framework to use"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Host port"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Author email"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode"),
    ai_customize: bool = typer.Option(False, "--ai", help="Enable AI customization"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """🚀 Create a new AI agent project.

    Generate a production-ready agent project with your choice of framework,
    complete with Docker support, configuration, and optional AI customization.

    Examples:
        # Interactive mode (default)
        $ watsonx-agent create

        # Quick mode with options
        $ watsonx-agent create --name my_agent --framework watsonx --port 8000

        # With AI customization
        $ watsonx-agent create --name chatbot --framework langraph --ai
    """
    # Setup logging
    setup_logging(log_level="DEBUG" if debug else "INFO", log_format="text")

    # Show banner
    _show_banner()

    try:
        if interactive:
            # Interactive mode
            config = _interactive_create()
        else:
            # Non-interactive mode - validate all required options
            if not all([name, framework, author, email]):
                console.print(
                    "[error]Error: In non-interactive mode, --name, --framework, --author, and --email are required[/]"
                )
                raise typer.Exit(code=1)

            config = _build_config_from_options(
                name=name,  # type: ignore
                framework=framework,  # type: ignore
                output=output,
                port=port,
                author=author,  # type: ignore
                email=email,  # type: ignore
                ai_customize=ai_customize,
            )

        # Generate agent
        asyncio.run(_generate_agent_async(config))

    except AgentCreatorError as e:
        console.print(f"[error]Error: {e.message}[/]")
        if debug and e.details:
            console.print(f"[dim]Details: {e.details}[/]")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[warning]Operation cancelled by user[/]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"[error]Unexpected error: {e}[/]")
        if debug:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command(name="list-frameworks")
def list_frameworks() -> None:
    """📋 List available agent frameworks.

    Display information about all supported frameworks including their
    descriptions and required dependencies.
    """
    _show_banner()

    table = Table(title="🎯 Available Frameworks", show_header=True, header_style="bold cyan")
    table.add_column("Framework", style="cyan", width=15)
    table.add_column("Name", style="green", width=25)
    table.add_column("Description", width=50)

    for framework in Framework:
        info = FrameworkInfo.from_framework(framework)
        table.add_row(
            framework.value,
            info.name,
            info.description,
        )

    console.print(table)
    console.print("\n[dim]Use --framework <name> when creating an agent[/]")


@app.command(name="info")
def show_info() -> None:
    """ℹ️  Show environment information and configuration.

    Display current configuration, environment variables, and system status.
    """
    _show_banner()

    settings = get_settings()

    info_table = Table(title="⚙️  Environment Information", show_header=True, header_style="bold cyan")
    info_table.add_column("Setting", style="cyan", width=30)
    info_table.add_column("Value", style="green")

    info_table.add_row("Base Path", str(settings.base_path))
    info_table.add_row("Assets Folder", str(settings.assets_folder))
    info_table.add_row("Output Folder", str(settings.output_folder))
    info_table.add_row("Default Framework", settings.default_framework)
    info_table.add_row("Default Port", str(settings.default_port))
    info_table.add_row("WatsonX Configured", "✅ Yes" if settings.has_watsonx_config else "❌ No")

    console.print(info_table)


def _show_banner() -> None:
    """Display application banner."""
    banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold white]🚀 WatsonX Agent Creator v{version}[/]                            [bold cyan]║[/]
[bold cyan]║[/]  [dim]Lightning-fast AI agent scaffolding for IBM watsonx.ai[/]  [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/]
    """.format(
        version=__version__
    )
    console.print(banner)


def _interactive_create() -> AgentConfig:
    """Interactive agent creation wizard.

    Returns:
        Complete agent configuration from user input
    """
    console.print("\n[bold cyan]📝 Agent Configuration Wizard[/]\n")

    # Get agent name
    while True:
        name = Prompt.ask("[prompt]Agent name (snake_case)[/]", default="my_agent")
        try:
            name = validate_agent_name(name)
            break
        except Exception as e:
            console.print(f"[error]{e}[/]")

    # Get framework
    console.print("\n[bold cyan]📦 Available Frameworks:[/]")
    for i, fw in enumerate(Framework, 1):
        console.print(f"  {i}. [cyan]{fw.display_name}[/] - {fw.description}")

    while True:
        try:
            choice = IntPrompt.ask("\n[prompt]Select framework[/]", default=1)
            if 1 <= choice <= len(Framework):
                framework = list(Framework)[choice - 1]
                break
            console.print("[error]Invalid choice[/]")
        except Exception as e:
            console.print(f"[error]{e}[/]")

    # Get author info (try from git config)
    default_author = _get_git_config("user.name") or "Developer"
    default_email = _get_git_config("user.email") or "dev@example.com"

    author = Prompt.ask("[prompt]Author name[/]", default=default_author)

    while True:
        email = Prompt.ask("[prompt]Author email[/]", default=default_email)
        try:
            email = validate_email(email)
            break
        except Exception as e:
            console.print(f"[error]{e}[/]")

    # Get port
    while True:
        try:
            port = IntPrompt.ask("[prompt]Host port[/]", default=8000)
            port = validate_port(port)
            break
        except Exception as e:
            console.print(f"[error]{e}[/]")

    # Get description
    description = Prompt.ask(
        "[prompt]Description (optional)[/]",
        default="",
    )

    # Get output path
    output_str = Prompt.ask(
        "[prompt]Output directory[/]",
        default="./agents",
    )
    output = Path(output_str)

    # AI customization
    ai_customize = False
    custom_task = ""

    settings = get_settings()
    if settings.has_watsonx_config:
        ai_customize = Confirm.ask(
            "\n[prompt]Enable AI-powered customization?[/]",
            default=False,
        )

        if ai_customize:
            custom_task = Prompt.ask(
                "[prompt]Describe what your agent should do[/]",
                default="",
            )

    # Build config
    metadata = ProjectMetadata(
        name=name,
        display_name=name.replace("_", " ").title(),
        description=description,
        author=author,
        author_email=email,
        framework=framework,
    )

    docker = DockerConfig(host_port=port)

    config = AgentConfig(
        metadata=metadata,
        output_path=output,
        docker=docker,
        enable_ai_customization=ai_customize,
        custom_task=custom_task,
    )

    # Show summary
    _show_config_summary(config)

    if not Confirm.ask("\n[prompt]Proceed with agent generation?[/]", default=True):
        console.print("[warning]Operation cancelled[/]")
        raise typer.Exit()

    return config


def _build_config_from_options(
    name: str,
    framework: str,
    output: Optional[Path],
    port: Optional[int],
    author: str,
    email: str,
    ai_customize: bool,
) -> AgentConfig:
    """Build config from command-line options.

    Args:
        name: Agent name
        framework: Framework name
        output: Output path
        port: Host port
        author: Author name
        email: Author email
        ai_customize: Enable AI customization

    Returns:
        Agent configuration
    """
    # Validate inputs
    name = validate_agent_name(name)
    email = validate_email(email)

    # Parse framework
    try:
        fw = Framework(framework.lower())
    except ValueError:
        console.print(f"[error]Invalid framework: {framework}[/]")
        console.print(f"[info]Available frameworks: {', '.join(f.value for f in Framework)}[/]")
        raise typer.Exit(code=1)

    # Validate port
    if port:
        port = validate_port(port)
    else:
        port = 8000

    # Build config
    metadata = ProjectMetadata(
        name=name,
        display_name=name.replace("_", " ").title(),
        author=author,
        author_email=email,
        framework=fw,
    )

    docker = DockerConfig(host_port=port)

    return AgentConfig(
        metadata=metadata,
        output_path=output or Path("./agents"),
        docker=docker,
        enable_ai_customization=ai_customize,
    )


def _show_config_summary(config: AgentConfig) -> None:
    """Display configuration summary.

    Args:
        config: Agent configuration
    """
    console.print("\n[bold cyan]📋 Configuration Summary:[/]")

    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Key", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("Name", config.metadata.name)
    summary_table.add_row("Framework", config.metadata.framework.display_name)
    summary_table.add_row("Author", f"{config.metadata.author} <{config.metadata.author_email}>")
    summary_table.add_row("Port", str(config.docker.host_port))
    summary_table.add_row("Output", str(config.output_path / config.metadata.name))
    summary_table.add_row("AI Customization", "✅ Enabled" if config.enable_ai_customization else "❌ Disabled")

    console.print(summary_table)


async def _generate_agent_async(config: AgentConfig) -> None:
    """Generate agent asynchronously with progress display.

    Args:
        config: Agent configuration
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating agent project...", total=None)

        # Initialize services
        ai_service = None
        if config.enable_ai_customization:
            try:
                ai_service = AIService(config.ai_model)
            except Exception as e:
                console.print(f"[warning]AI service unavailable: {e}[/]")

        generator = AgentGenerator(ai_service=ai_service)

        # Generate agent
        response = await generator.generate_agent(config)

        progress.update(task, completed=True)

    # Show result
    if response.success:
        console.print(
            Panel(
                f"[success]{response.message}[/]\n\n"
                f"[dim]Location:[/] [cyan]{response.output_path}[/]\n"
                f"[dim]Framework:[/] [cyan]{response.framework.display_name}[/]\n"
                f"[dim]Port:[/] [cyan]{response.metadata.get('port', 'N/A')}[/]\n\n"
                f"[bold]Next steps:[/]\n"
                f"1. cd {response.output_path}\n"
                f"2. Configure .env with your WatsonX credentials\n"
                f"3. docker-compose up\n"
                f"4. Visit http://localhost:{response.metadata.get('port', 8000)}/docs",
                title="✨ Success!",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[error]{response.message}[/]\n\n"
                f"[dim]Error:[/] {response.error}",
                title="❌ Generation Failed",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)


def _get_git_config(key: str) -> Optional[str]:
    """Get git config value.

    Args:
        key: Git config key (e.g., 'user.name')

    Returns:
        Config value or None if not found
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        console.print(f"[error]Fatal error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Tests for CLI application.

This module tests the Typer CLI interface.
"""

from typer.testing import CliRunner

from watsonx_agent_creator.cli.app import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_help_command(self) -> None:
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "watsonx-agent" in result.stdout.lower()

    def test_version_command(self) -> None:
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "WatsonX Agent Creator" in result.stdout

    def test_list_frameworks_command(self) -> None:
        """Test list-frameworks command."""
        result = runner.invoke(app, ["list-frameworks"])
        assert result.exit_code == 0
        assert "watsonx" in result.stdout.lower()
        assert "langraph" in result.stdout.lower()

    def test_info_command(self) -> None:
        """Test info command."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Environment Information" in result.stdout

    def test_create_non_interactive_missing_args(self) -> None:
        """Test create command without required args in non-interactive mode."""
        result = runner.invoke(
            app,
            ["create", "--no-interactive", "--name", "test_agent"],
        )
        # Should fail because other required args are missing
        assert result.exit_code == 1
        assert "required" in result.stdout.lower()

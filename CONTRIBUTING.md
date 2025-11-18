# Contributing to WatsonX Agent Creator

First off, thank you for considering contributing to WatsonX Agent Creator! It's people like you that make this tool a great resource for the community.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed feature**
- **Explain why this enhancement would be useful**
- **List some examples of how it would be used**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes** (`make test`)
5. **Ensure code quality checks pass** (`make audit`)
6. **Update documentation** if needed
7. **Write a clear commit message**

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or 3.12
- [UV](https://github.com/astral-sh/uv) package manager
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/watsonx-agent-creator.git
cd watsonx-agent-creator

# Install development dependencies
make dev-install

# Create a new branch for your feature
git checkout -b feature/amazing-feature
```

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests quickly without coverage
make test-quick

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestFramework::test_framework_values -v
```

### Code Quality

```bash
# Run all quality checks
make audit

# Format code
make format

# Run linter
make lint

# Type checking
make type-check
```

## 📝 Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Maximum line length: 100 characters
- Use double quotes for strings

### Type Hints

- **100% type coverage required**
- Use type hints for all function parameters and return values
- Use `from typing import` for generic types
- Use Pydantic models for data validation

Example:
```python
from pathlib import Path
from typing import Optional

def process_file(file_path: Path, encoding: str = "utf-8") -> Optional[str]:
    """Process a file and return its contents.

    Args:
        file_path: Path to the file to process
        encoding: File encoding (default: utf-8)

    Returns:
        File contents or None if file doesn't exist
    """
    ...
```

### Documentation

- Use Google-style docstrings for all modules, classes, and functions
- Include `Args:`, `Returns:`, `Raises:`, and `Examples:` sections where applicable
- Keep docstrings up to date with code changes

Example:
```python
def generate_agent(config: AgentConfig) -> AgentGenerationResponse:
    """Generate a complete AI agent project.

    This function orchestrates the entire agent generation process including
    template rendering, file operations, and optional AI customization.

    Args:
        config: Complete agent configuration with metadata and settings

    Returns:
        Generation response with status, path, and metadata

    Raises:
        GenerationError: If project generation fails
        ValidationError: If configuration is invalid

    Examples:
        >>> config = AgentConfig(...)
        >>> response = generate_agent(config)
        >>> print(response.output_path)
        /home/user/agents/my_agent
    """
    ...
```

### Testing

- Write tests for all new features and bug fixes
- Aim for >80% code coverage
- Use pytest fixtures for common test setup
- Use descriptive test names that explain what is being tested

Example:
```python
class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_valid_config_creation(self, sample_metadata: ProjectMetadata) -> None:
        """Test that valid configuration can be created successfully."""
        config = AgentConfig(
            metadata=sample_metadata,
            output_path=Path("/tmp/agents"),
        )

        assert config.metadata.name == "test_agent"
        assert config.output_path.is_absolute()

    def test_invalid_name_raises_validation_error(self) -> None:
        """Test that invalid agent names raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectMetadata(
                name="Invalid-Name",  # Hyphens not allowed
                ...
            )

        assert "lowercase" in str(exc_info.value)
```

### Async Code

- Use `async`/`await` for I/O operations
- Use `asyncio` for concurrent operations
- Use `aiofiles` for file operations
- Properly handle exceptions in async contexts

Example:
```python
async def read_template(path: Path) -> str:
    """Read template file asynchronously.

    Args:
        path: Path to template file

    Returns:
        Template contents

    Raises:
        FileOperationError: If file cannot be read
    """
    try:
        async with aiofiles.open(path, "r") as f:
            return await f.read()
    except OSError as e:
        raise FileOperationError(f"Failed to read template: {path}") from e
```

## 🎯 Project Structure

```
watsonx-agent-creator/
├── src/watsonx_agent_creator/
│   ├── cli/              # Typer CLI application
│   ├── core/             # Configuration, logging, exceptions
│   ├── domain/           # Pydantic models and schemas
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── assets/               # Template assets
├── pyproject.toml        # Project configuration
├── Makefile             # Development commands
└── README.md            # Documentation
```

### Adding New Features

1. **Determine the right location** based on the feature type:
   - CLI commands → `cli/app.py`
   - Business logic → `services/`
   - Data models → `domain/`
   - Configuration → `core/config.py`
   - Utilities → `utils/`

2. **Create the feature** following our coding standards

3. **Add tests** in the corresponding `tests/test_*.py` file

4. **Update documentation** in README.md if user-facing

### Adding New Frameworks

To add support for a new agent framework:

1. Create framework directory:
   ```bash
   mkdir -p assets/frameworks/your_framework/model
   ```

2. Add agent template (`assets/frameworks/your_framework/model/agent.py`)

3. Add dependencies (optional):
   ```toml
   # assets/frameworks/your_framework/pyproject.fragment.toml
   [project]
   dependencies = [
       "your-framework>=1.0.0",
   ]
   ```

4. Update `Framework` enum in `src/watsonx_agent_creator/domain/models.py`:
   ```python
   class Framework(str, Enum):
       ...
       YOUR_FRAMEWORK = "your_framework"
   ```

5. Add framework description and dependencies

6. Add tests for the new framework

7. Update README.md

## 🔄 Git Workflow

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add support for new framework`
- `fix: resolve template rendering issue`
- `docs: update installation instructions`
- `test: add tests for AI service`
- `refactor: simplify configuration loading`
- `chore: update dependencies`

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

### Pull Request Process

1. **Update your branch** with the latest `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main
   ```

2. **Ensure all checks pass**:
   ```bash
   make audit
   make test
   ```

3. **Push your changes**:
   ```bash
   git push origin your-branch
   ```

4. **Create a Pull Request** with:
   - Clear title following commit message conventions
   - Detailed description of changes
   - Reference to related issues
   - Screenshots if UI changes

5. **Address review feedback** promptly

6. **Squash commits** if requested before merging

## 📋 Code Review Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines (Ruff passes)
- [ ] Type hints are complete (MyPy passes)
- [ ] Tests are added and passing
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No debugging code or print statements
- [ ] Error handling is appropriate
- [ ] Async operations are properly awaited
- [ ] Code is DRY (Don't Repeat Yourself)

## 🐛 Debugging

### Running in Debug Mode

```bash
# Enable debug logging
watsonx-agent create --debug

# Or set environment variable
export LOG_LEVEL=DEBUG
watsonx-agent create
```

### Common Issues

1. **Import errors**: Ensure you've run `make install` or `make dev-install`
2. **Test failures**: Run `make clean` and `make test` again
3. **Type errors**: Run `make type-check` to see detailed errors
4. **Linting errors**: Run `make format` to auto-fix many issues

## 💬 Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/ruslanmv/watsonx-agent-creator/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/ruslanmv/watsonx-agent-creator/issues)
- **Security**: Email security concerns to contact@ruslanmv.com

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy Contributing! 🚀**

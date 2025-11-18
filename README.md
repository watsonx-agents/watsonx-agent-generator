<div align="center">

# ⚡ WatsonX Agent Creator

### Lightning-fast AI agent scaffolding for IBM watsonx.ai

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 The Why

Building production-ready AI agents shouldn't take hours of boilerplate setup. **WatsonX Agent Creator** is a category-defining CLI tool that generates complete, containerized agent projects in seconds—not hours.

Forget manual configuration, dependency hell, and template copying. This tool provides:

✨ **Beautiful CLI** with interactive wizards and rich formatting
🚀 **Lightning-fast** dependency resolution using UV
🤖 **AI-powered** code customization with IBM Granite models
🐳 **Docker-ready** projects with compose files
🎨 **Multiple frameworks** - WatsonX, LangGraph, CrewAI, BeeAI, and more
📦 **Production-grade** structure with type hints, tests, and docs
🔒 **Type-safe** with Pydantic V2 validation
🎯 **Zero-config** deployment - just generate and run

## ✨ Features

### 🎯 **Intelligent Agent Generation**
- **Interactive CLI wizard** with beautiful formatting (powered by Rich)
- **Multiple framework support** - Choose from 6+ agent frameworks
- **AI-powered customization** using IBM Granite models
- **Smart validation** with detailed error messages

### 🚀 **Modern Tech Stack**
- **UV** for lightning-fast dependency management
- **Typer + Rich** for beautiful terminal UX
- **Pydantic V2** for strict type validation
- **Ruff** for aggressive linting and formatting
- **MyPy** for complete type safety
- **Async/await** throughout for high performance

### 📦 **Production-Ready Output**
- **Complete project structure** with configs, tests, and docs
- **Docker & Docker Compose** files included
- **FastAPI** application scaffold
- **Structured logging** with JSON support
- **Environment management** with .env files
- **Git initialization** with proper .gitignore

### 🎨 **Supported Frameworks**

| Framework | Description | Dependencies |
|-----------|-------------|--------------|
| **WatsonX SDK** | Native IBM WatsonX.ai SDK for direct model access | `ibm-watsonx-ai` |
| **LangGraph** | Build stateful, multi-actor applications with LLMs | `langgraph`, `langchain-ibm` |
| **CrewAI** | Framework for orchestrating role-playing autonomous AI agents | `crewai` |
| **BeeAI** | Production-ready agent framework with observability | `beeai-framework` |
| **LangFlow** | Visual programming interface for LangChain | `langflow` |
| **Base** | Minimal template for custom implementations | None |

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or 3.12
- [UV](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerization)
- IBM WatsonX account (optional, for AI features)

### Installation

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/ruslanmv/watsonx-agent-creator.git
cd watsonx-agent-creator

# Install the package
make install

# Or for development
make dev-install
```

### Create Your First Agent

#### Interactive Mode (Recommended)

```bash
watsonx-agent create
```

The beautiful CLI wizard will guide you through:
1. 📝 Choosing an agent name
2. 🎨 Selecting a framework
3. 👤 Entering author information
4. ⚙️ Configuring ports and settings
5. 🤖 Optional AI-powered customization

#### Quick Mode

```bash
# Create a WatsonX agent quickly
watsonx-agent create \
  --name my_agent \
  --framework watsonx \
  --author "Your Name" \
  --email "you@example.com" \
  --port 8000 \
  --no-interactive

# With AI customization
watsonx-agent create \
  --name chatbot \
  --framework langraph \
  --ai \
  --no-interactive
```

### Run Your Agent

```bash
cd agents/my_agent

# Configure environment
cp .env.sample .env
# Edit .env with your WatsonX credentials

# Run with Docker
docker-compose up

# Or run directly
cd app
uv pip install -e .
uvicorn my_agent.main:app --reload
```

Visit `http://localhost:8000/docs` for the auto-generated API documentation!



## 📚 Documentation

### Available Commands

```bash
# Create a new agent (interactive wizard)
watsonx-agent create

# Create with options (non-interactive)
watsonx-agent create --name my_agent --framework watsonx

# List available frameworks
watsonx-agent list-frameworks

# Show environment info
watsonx-agent info

# Show version
watsonx-agent --version
```

### Development Commands

```bash
# Install dependencies
make install          # Production dependencies
make dev-install      # Development dependencies

# Code quality
make audit           # Run all quality checks
make lint            # Run linter
make format          # Format code
make type-check      # Run type checker

# Testing
make test            # Run tests with coverage
make test-quick      # Run tests without coverage

# Building
make build           # Build distribution packages
make docker-build    # Build Docker image

# Cleaning
make clean           # Remove build artifacts
```

### Generated Project Structure

```
agents/my_agent/
├── app/
│   ├── my_agent/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── configs/             # Configuration management
│   │   │   ├── logger.py
│   │   │   ├── settings.py
│   │   │   └── constants.py
│   │   └── model/
│   │       └── agent.py         # Your agent logic
│   └── pyproject.toml           # Project dependencies (PEP 621)
├── tests/                       # Test directory
│   └── __init__.py
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Docker Compose configuration
├── .env.sample                  # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```



### AI-Powered Customization

When creating an agent, you can optionally enable AI-powered customization:

```bash
watsonx-agent create --ai
```

The tool will:
1. 🤖 Use IBM Granite models to understand your requirements
2. ✍️ Generate customized agent code based on your task description
3. ✅ Validate the generated code for syntax errors
4. 📝 Apply the customization to your project

**Example:**
```
Task: Create a chatbot that answers questions about Python programming

The AI will generate a complete agent implementation with:
- Question answering logic
- Context management
- Error handling
- Type hints and docstrings
```


## 🏗️ Architecture

### Clean Architecture Principles

The tool follows clean architecture with clear separation of concerns:

- **CLI Layer** (`cli/`) - Typer + Rich for beautiful user interaction
- **Core Layer** (`core/`) - Configuration, logging, exception handling
- **Domain Layer** (`domain/`) - Business models and schemas (Pydantic V2)
- **Services Layer** (`services/`) - Business logic (generator, AI, templates)
- **Utils Layer** (`utils/`) - Shared utilities and validators

### Key Design Patterns

- **Dependency Injection** - Services are injected, not instantiated
- **Repository Pattern** - Template and file operations abstracted
- **Strategy Pattern** - Framework-specific logic encapsulated
- **Builder Pattern** - Complex object construction simplified
- **Singleton Pattern** - Settings cached for performance

## 🤝 Contributing

We welcome contributions! Whether it's:

- 🐛 Bug reports and fixes
- ✨ New features and frameworks
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🧪 Test coverage

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Adding a New Framework

1. Create framework directory:
   ```bash
   mkdir -p assets/frameworks/your_framework/model
   ```

2. Add agent template:
   ```bash
   # Create assets/frameworks/your_framework/model/agent.py
   ```

3. Add dependencies (optional):
   ```bash
   # Create assets/frameworks/your_framework/pyproject.fragment.toml
   ```

4. Update framework enum in `src/watsonx_agent_creator/domain/models.py`

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ruslan Magana**

- Website: [ruslanmv.com](https://ruslanmv.com)
- GitHub: [@ruslanmv](https://github.com/ruslanmv)

## 🙏 Acknowledgments

- IBM WatsonX.ai team for the amazing AI platform
- The open-source community for the fantastic tools
- All contributors who help improve this project

## ⭐ Star History

If you find this project useful, please consider giving it a star! It helps others discover this tool.

---

<div align="center">

**Made with ❤️ by [Ruslan Magana](https://ruslanmv.com)**

[Report Bug](https://github.com/ruslanmv/watsonx-agent-creator/issues) • [Request Feature](https://github.com/ruslanmv/watsonx-agent-creator/issues) • [Discussions](https://github.com/ruslanmv/watsonx-agent-creator/discussions)

</div>


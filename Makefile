.PHONY: help install dev-install start test audit lint format clean build docker-build docker-run

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## 📖 Show this help message
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  🚀 WatsonX Agent Creator - Development Commands        ║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## 📦 Install production dependencies using UV
	@echo "$(BLUE)Installing production dependencies with UV...$(NC)"
	@uv pip install -e .
	@echo "$(GREEN)✓ Installation complete!$(NC)"

dev-install: ## 🛠️  Install development dependencies using UV
	@echo "$(BLUE)Installing development dependencies with UV...$(NC)"
	@uv pip install -e ".[dev]"
	@pre-commit install
	@echo "$(GREEN)✓ Development environment ready!$(NC)"

start: ## ▶️  Run the CLI application
	@echo "$(BLUE)Starting WatsonX Agent Creator...$(NC)"
	@watsonx-agent --help

test: ## 🧪 Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	@pytest tests/ -v --cov --cov-report=term-missing

test-quick: ## ⚡ Run tests without coverage
	@pytest tests/ -v

audit: ## 🔍 Run comprehensive code quality checks
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Running Code Quality Audit                             ║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)1/4 Running Ruff linter...$(NC)"
	@ruff check src/ tests/ || true
	@echo ""
	@echo "$(YELLOW)2/4 Running Ruff formatter check...$(NC)"
	@ruff format --check src/ tests/ || true
	@echo ""
	@echo "$(YELLOW)3/4 Running MyPy type checker...$(NC)"
	@mypy src/ || true
	@echo ""
	@echo "$(YELLOW)4/4 Running security checks...$(NC)"
	@ruff check --select S src/ || true
	@echo ""
	@echo "$(GREEN)✓ Audit complete!$(NC)"

lint: ## 🔧 Run linter (Ruff)
	@echo "$(BLUE)Running Ruff linter...$(NC)"
	@ruff check src/ tests/
	@echo "$(GREEN)✓ Linting complete!$(NC)"

format: ## ✨ Format code with Ruff
	@echo "$(BLUE)Formatting code with Ruff...$(NC)"
	@ruff check --fix src/ tests/
	@ruff format src/ tests/
	@echo "$(GREEN)✓ Code formatted!$(NC)"

type-check: ## 🔎 Run type checking with MyPy
	@echo "$(BLUE)Running MyPy type checker...$(NC)"
	@mypy src/
	@echo "$(GREEN)✓ Type checking complete!$(NC)"

clean: ## 🧹 Clean build artifacts and cache
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf htmlcov/
	@rm -rf .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

build: clean ## 🏗️  Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	@uv build
	@echo "$(GREEN)✓ Build complete! Check dist/ folder$(NC)"

docker-build: ## 🐳 Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t watsonx-agent-creator:latest .
	@echo "$(GREEN)✓ Docker image built!$(NC)"

docker-run: ## 🚀 Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	@docker run -it --rm \
		-v $(PWD)/agents:/app/agents \
		-v $(PWD)/.env:/app/.env \
		watsonx-agent-creator:latest

publish-test: build ## 📤 Publish to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(NC)"
	@uv publish --repository testpypi
	@echo "$(GREEN)✓ Published to Test PyPI!$(NC)"

publish: build ## 🚀 Publish to PyPI
	@echo "$(RED)Publishing to PyPI...$(NC)"
	@uv publish
	@echo "$(GREEN)✓ Published to PyPI!$(NC)"

dev: dev-install ## 🔄 Complete development setup
	@echo "$(GREEN)✓ Development environment is ready!$(NC)"
	@echo "$(BLUE)Run 'make start' to begin$(NC)"

ci: lint type-check test ## 🤖 Run CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline completed successfully!$(NC)"

watch-test: ## 👀 Watch for changes and run tests
	@echo "$(BLUE)Watching for changes...$(NC)"
	@pytest-watch tests/

.DEFAULT_GOAL := help

# Docker Variables
DOCKER_REGISTRY := shahadathhs
DOCKER_IMAGE := $(DOCKER_REGISTRY)/ecoroute:latest
COMPOSE_FILE := compose.yaml

# Python Variables
VENV := .venv
PYTHON_BIN := uv run python

# Phony targets
.PHONY: help setup venv install reset-venv pre-commit-install pre-commit-run pre-commit-update
.PHONY: bump-major bump-minor bump-patch build release
.PHONY: dev dev-verbose prod
.PHONY: lint lint-fix format format-check type-check check-all fix-all
.PHONY: migrate-up migrate-down migration db-shell
.PHONY: docker-build docker-infra docker-prod docker-down docker-logs
.PHONY: clean shell logs update freeze list add remove ci info

.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;32m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# SETUP
# =============================================================================
venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	@rm -rf .venv 2>/dev/null || true
	@uv venv
	@echo "✓ Virtual environment created"

reset-venv: ## Force reset virtual environment (fix permission issues)
	@echo "Resetting virtual environment..."
	@rm -rf .venv .uv uv.lock 2>/dev/null || true
	@uv venv
	@uv sync
	@echo "✓ Virtual environment reset complete"

install: ## Install dependencies
	@echo "Installing dependencies..."
	@uv sync
	@echo "✓ Dependencies installed"

setup: venv install ## Full setup (venv + install)
	@echo "✓ Setup complete!"

pre-commit-install: ## Install pre-commit hooks
	@echo "Installing pre-commit hooks..."
	@uv run pre-commit install
	@echo "✓ Pre-commit hooks installed"

pre-commit-run: ## Run all pre-commit hooks manually
	@echo "Running pre-commit hooks..."
	@uv run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "Updating pre-commit hooks..."
	@uv run pre-commit autoupdate
	@echo "✓ Pre-commit hooks updated"

# =============================================================================
# VERSION MANAGEMENT
# =============================================================================
bump-major: ## Bump major version
	@echo "Bumping major version..."
	@uv run bump-my-version major
	@echo "✓ Bumped to major version $$(grep -m1 'version = ' pyproject.toml | cut -d'"' -f2)"

bump-minor: ## Bump minor version
	@echo "Bumping minor version..."
	@uv run bump-my-version minor
	@echo "✓ Bumped to minor version $$(grep -m1 'version = ' pyproject.toml | cut -d'"' -f2)"

bump-patch: ## Bump patch version
	@echo "Bumping patch version..."
	@uv run bump-my-version patch
	@echo "✓ Bumped to patch version $$(grep -m1 'version = ' pyproject.toml | cut -d'"' -f2)"

build: ## Build distribution packages
	@echo "Building distribution packages..."
	@uv run python -m build
	@echo "✓ Built packages in dist/"

release: bump-patch build ## Create patch release (bump + build)
	@echo "✓ Release $$(grep -m1 'version = ' pyproject.toml | cut -d'"' -f2) ready"
	@echo "Run 'git push --tags' to publish"

# =============================================================================
# RUNNING
# =============================================================================
dev: ## Run in development mode with hot reload
	$(PYTHON_BIN) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-verbose: ## Run in development mode with verbose logging
	$(PYTHON_BIN) -m uvicorn app.main:app --reload --log-level debug

prod: ## Run in production mode
	$(PYTHON_BIN) -m uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8000} --workers 4

# =============================================================================
# CODE QUALITY
# =============================================================================
lint: ## Run linter (ruff)
	$(PYTHON_BIN) -m ruff check app/

lint-fix: ## Fix linting issues automatically
	$(PYTHON_BIN) -m ruff check --fix app/

format: ## Format code with black
	$(PYTHON_BIN) -m black app/

format-check: ## Check if code needs formatting
	$(PYTHON_BIN) -m black --check app/

type-check: ## Run type checker (mypy)
	$(PYTHON_BIN) -m mypy app/

check-all: lint type-check ## Run all quality checks

fix-all: lint-fix format ## Fix all auto-fixable issues

# =============================================================================
# DATABASE
# =============================================================================
migrate-up: ## Run database migrations
	$(PYTHON_BIN) -m alembic upgrade head

migrate-down: ## Rollback database migrations
	$(PYTHON_BIN) -m alembic downgrade -1

migration: ## Create new migration (use NAME=name)
	$(PYTHON_BIN) -m alembic revision --autogenerate -m "$(NAME)"

db-shell: ## Open database shell
	psql $${DATABASE_URL}

# =============================================================================
# DOCKER
# =============================================================================
docker-build: ## Build Docker image
	docker builder build -t $(DOCKER_IMAGE) .

docker-infra: ## Start Docker infrastructure containers (DB, Qdrant)
	docker compose --profile infra up -d

docker-prod: ## Start full Docker production stack
	docker compose --profile prod up -d

docker-down: ## Stop Docker containers
	docker compose --profile prod down

docker-logs: ## Show Docker logs
	docker compose logs -f

# =============================================================================
# UTILITIES
# =============================================================================
clean: ## Clean up generated files
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" -o -name ".mypy_cache" \) -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" -o -name ".coverage" \) -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ htmlcov/ logs/ .venv/ .uv/ uv.lock

shell: ## Open Python shell with app context
	$(PYTHON_BIN) -i -c "from app.main import app; from app.core.config import settings; print('App loaded!')"

logs: ## Show application logs
	@tail -f logs/app.log 2>/dev/null || echo "No log file found"

update: ## Update dependencies
	uv sync --upgrade

freeze: ## Update lock file
	uv lock

list: ## List installed dependencies
	uv pip list

add: ## Add a new package (use PKG=name)
	uv add $(PKG)

remove: ## Remove a package (use PKG=name)
	uv remove $(PKG)

# =============================================================================
# CI/CD
# =============================================================================
ci: lint type-check ## Run CI pipeline checks

# =============================================================================
# INFO
# =============================================================================
info: ## Show project information
	@echo "Name: EcoRoute Atlas"
	@echo "Python: $(shell python --version)"
	@echo "Environment: $${ENVIRONMENT:-development}"
	@echo "Database: $${DATABASE_URL:-postgresql://localhost:5432/ecoroute}"
	@echo "Qdrant: $${QDRANT_HOST:-localhost}:$${QDRANT_PORT:-6333}"

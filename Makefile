# Docker Variables
DOCKER_REGISTRY := shahadathhs
DOCKER_IMAGE := $(DOCKER_REGISTRY)/ecoroute:latest
COMPOSE_FILE := compose.yaml

# Python Variables
VENV := .venv
PYTHON_BIN := uv run python

# Phony targets
.PHONY: help setup venv install reset-venv pre-commit-install pre-commit-run pre-commit-update
.PHONY: build dev dev-verbose prod release-dry-run release-changelog release-publish
.PHONY: lint lint-fix format format-check type-check check-all fix-all
.PHONY: migrate-up migrate-down migration db-shell
.PHONY: docker-build docker-infra docker-prod docker-down docker-logs
.PHONY: clean shell logs sync update upgrade-all-pinned freeze list outdated check compile export why tree add remove ci info

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
# RUNNING
# =============================================================================
build: ## Build distribution packages
	@echo "Building distribution packages..."
	@uv run python -m build
	@echo "✓ Built packages in dist/"

dev: ## Run in development mode with hot reload
	$(PYTHON_BIN) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-verbose: ## Run in development mode with verbose logging
	$(PYTHON_BIN) -m uvicorn app.main:app --reload --log-level debug

prod: ## Run in production mode
	$(PYTHON_BIN) -m uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8000} --workers 4

release-dry-run: ## Preview release without publishing (semantic-release)
	@echo "Previewing release..."
	@uv run semantic-release version --no-commit --no-tag

release-changelog: ## Generate changelog only (semantic-release)
	@echo "Generating changelog..."
	@uv run semantic-release changelog

release-publish: ## Publish release (semantic-release - used by CI)
	@echo "Publishing release..."
	@uv run semantic-release version --vcs-release

# =============================================================================

# CODE QUALITY
# =============================================================================
lint: ## Run linter (ruff)
	@echo "Running linter..."
	$(PYTHON_BIN) -m ruff check app/
	@echo "✓ Linting complete"

lint-fix: ## Fix linting issues automatically
	@echo "Fixing linting issues..."
	$(PYTHON_BIN) -m ruff check --fix app/

format: ## Format code with black
	@echo "Formatting code..."
	$(PYTHON_BIN) -m black app/
	@echo "✓ Code formatted"

format-check: ## Check if code needs formatting
	@echo "Checking code formatting..."
	$(PYTHON_BIN) -m black --check app/

type-check: ## Run type checker (mypy)
	@echo "Running type checks..."
	$(PYTHON_BIN) -m mypy app/

check-all: lint type-check ## Run all quality checks
	@echo "Running all quality checks..."

fix-all: lint-fix format ## Fix all auto-fixable issues
	@echo "Fixing all auto-fixable issues..."

# =============================================================================
# DATABASE
# =============================================================================
migrate-up: ## Run database migrations
	@echo "Running database migrations..."
	$(PYTHON_BIN) -m alembic upgrade head
	@echo "✓ Migrations applied"

migrate-down: ## Rollback database migrations
	@echo "Rolling back migrations..."
	$(PYTHON_BIN) -m alembic downgrade -1

migration: ## Create new migration (use NAME=name)
	@echo "Creating migration: $(NAME)..."
	$(PYTHON_BIN) -m alembic revision --autogenerate -m "$(NAME)"

db-shell: ## Open database shell
	@echo "Opening database shell..."
	psql $${DATABASE_URL}

# =============================================================================
# DOCKER
# =============================================================================
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker builder build -t $(DOCKER_IMAGE) .

docker-infra: ## Start Docker infrastructure containers (DB, Qdrant)
	@echo "Starting infrastructure containers..."
	docker compose --profile infra up -d

docker-prod: ## Start full Docker production stack
	@echo "Starting production stack..."
	docker compose --profile prod up -d

docker-down: ## Stop Docker containers
	@echo "Stopping Docker containers..."
	docker compose --profile prod down

docker-logs: ## Show Docker logs
	docker compose logs -f

# =============================================================================
# UTILITIES
# =============================================================================
clean: ## Clean up generated files
	@echo "Cleaning up generated files..."
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" -o -name ".mypy_cache" \) -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" -o -name ".coverage" \) -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ htmlcov/ logs/ .venv/ .uv/ uv.lock
	@echo "✓ Cleanup complete"

shell: ## Open Python shell with app context
	@echo "Loading Python shell..."
	$(PYTHON_BIN) -i -c "from app.main import app; from app.core.config import settings; print('App loaded!')"

logs: ## Show application logs
	@tail -f logs/app.log 2>/dev/null || echo "No log file found"

sync: ## Sync dependencies to lock file
	@echo "Syncing dependencies..."
	uv sync
	@echo "✓ Dependencies synced"

update: ## Update lock file within pyproject.toml constraints
	@echo "Updating lock file (within current version constraints)..."
	uv lock --upgrade
	uv sync
	@echo "✓ Lock file updated"

upgrade-all-pinned: ## Convert all pinned versions (==) to flexible versions (>=)
	@echo "Converting pinned versions to flexible versions..."
	@sed -i 's/"\([a-zA-Z0-9-]*\)==\([0-9.]*\)"/"\1>=\2"/g' pyproject.toml
	@echo "✓ Converted == to >= in pyproject.toml"
	@echo "Run 'make update' to upgrade to latest versions"

freeze: ## Update lock file
	@echo "Updating lock file..."
	uv lock

list: ## List installed dependencies
	uv pip list

add: ## Add a new package (use PKG=name)
	@echo "Adding package: $(PKG)..."
	uv add $(PKG)

add-dev: ## Add a new dev package (use PKG=name)
	@echo "Adding dev package: $(PKG)..."
	uv add --dev $(PKG)

remove: ## Remove a package (use PKG=name)
	@echo "Removing package: $(PKG)..."
	uv remove $(PKG)

outdated: ## Check for outdated dependencies
	@echo "Checking for outdated dependencies..."
	uv pip list --outdated

check: ## Check for dependency conflicts
	@echo "Checking for dependency conflicts..."
	uv pip check

compile: ## Compile requirements.txt from pyproject.toml
	@echo "Compiling requirements.txt..."
	uv pip compile pyproject.toml -o requirements.txt

export: ## Export locked dependencies to requirements.txt
	@echo "Exporting dependencies to requirements.txt..."
	uv pip export -o requirements.txt

why: ## Show why a package is installed (use PKG=name)
	@echo "Checking why $(PKG) is installed..."
	uv pip tree --package $(PKG)

tree: ## Show dependency tree
	@echo "Showing dependency tree..."
	uv pip tree

# =============================================================================
# CI/CD
# =============================================================================
security: ## Run security scan with bandit
	@echo "Running security scan..."
	@uv run bandit -r app/ -f screen -v
	@echo "✓ Security scan complete"

ci: pre-commit-run security build ## Run CI pipeline checks
	@echo "Running CI pipeline..."

# =============================================================================
# INFO
# =============================================================================
info: ## Show project information
	@echo "Name: EcoRoute Atlas"
	@echo "Python: $(shell python --version)"
	@echo "Environment: $${ENVIRONMENT:-development}"
	@echo "Database: $${DATABASE_URL:-postgresql://localhost:5432/ecoroute}"
	@echo "Qdrant: $${QDRANT_HOST:-localhost}:$${QDRANT_PORT:-6333}"

# Docker Variables
DOCKER_REGISTRY := shahadathhs
DOCKER_IMAGE := $(DOCKER_REGISTRY)/ecoroute:latest
COMPOSE_FILE := compose.yaml

# Python Variables
VENV := .venv
PYTHON_BIN := uv run python

# Phony targets
.PHONY: help setup venv install
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
	uv venv --clear

install: ## Install dependencies
	uv sync

setup: venv install ## Full setup (venv + install)

# =============================================================================
# RUNNING
# =============================================================================
dev: ## Run in development mode with hot reload
	$(PYTHON_BIN) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-verbose: ## Run in development mode with verbose logging
	$(PYTHON_BIN) -m uvicorn app.main:app --reload --log-level debug

prod: ## Run in production mode
	$(PYTHON_BIN) -m uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8000} --workers $${WORKERS:-4}

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
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ *.egg-info/ htmlcov/
	rm -rf logs/*.log.* .venv .uv logs uv.lock

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

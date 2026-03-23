# Docker Variables
DOCKER_REGISTRY := shahadathhs
DOCKER_IMAGE := $(DOCKER_REGISTRY)/ecoroute:latest
COMPOSE_FILE := compose.yaml

# Phony targets
.PHONY: help install run dev lint format clean migrate-up migrate-down shell db-shell

# Default target
.DEFAULT_GOAL := help

# Variables
SHELL := /bin/bash
PYTHON := $(shell command -v python3.14 || command -v python3.13 || command -v python3.12 || command -v python3.11 || echo python)
VENV := ecoroute_venv
PIP := $(VENV)/bin/pip
ACTIVATE := $(VENV)/bin/activate
PYTHON_BIN := $(VENV)/bin/python

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo -e "$(BLUE)EcoRoute Atlas - Available Commands:$(NC)"
	@echo -e ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo -e ""

## Development Setup
install: ## Install dependencies
	@echo -e "$(BLUE)Installing dependencies...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo -e "$(GREEN)✓ Dependencies installed$(NC)"

venv: ## Create virtual environment
	@echo -e "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo -e "$(GREEN)✓ Virtual environment created$(NC)"
	@echo -e "$(YELLOW)Activate with: source $(ACTIVATE)$(NC)"

setup: venv install ## Full setup (venv + install)
	@echo -e "$(GREEN)✓ Setup complete! Activate with: source $(ACTIVATE)$(NC)"

## Running the Application
dev: ## Run in development mode with hot reload
	@echo -e "$(BLUE)Starting development server...$(NC)"
	@$(PYTHON_BIN) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-verbose: ## Run in development mode with verbose logging
	@echo -e "$(BLUE)Starting development server (verbose)...$(NC)"
	@$(PYTHON_BIN) -m uvicorn app.main:app --reload --log-level debug

prod: ## Run in production mode
	@echo -e "$(BLUE)Starting production server...$(NC)"
	@$(PYTHON_BIN) -m uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8000} --workers $${WORKERS:-4}

## Code Quality
lint: ## Run linter (ruff)
	@echo -e "$(BLUE)Linting code...$(NC)"
	@$(PYTHON_BIN) -m ruff check app/

lint-fix: ## Fix linting issues automatically
	@echo -e "$(BLUE)Fixing linting issues...$(NC)"
	@$(PYTHON_BIN) -m ruff check --fix app/

format: ## Format code with black
	@echo -e "$(BLUE)Formatting code...$(NC)"
	@$(PYTHON_BIN) -m black app/

format-check: ## Check if code needs formatting
	@echo -e "$(BLUE)Checking code formatting...$(NC)"
	@$(PYTHON_BIN) -m black --check app/

type-check: ## Run type checker (mypy)
	@echo -e "$(BLUE)Running type checks...$(NC)"
	@$(PYTHON_BIN) -m mypy app/

check-all: lint type-check ## Run all quality checks
	@echo -e "$(GREEN)✓ All checks passed$(NC)"

fix-all: lint-fix format ## Fix all auto-fixable issues
	@echo -e "$(GREEN)✓ Code fixed$(NC)"

## Database
migrate-up: ## Run database migrations
	@echo -e "$(BLUE)Running migrations...$(NC)"
	@$(PYTHON_BIN) -m alembic upgrade head

migrate-down: ## Rollback database migrations
	@echo -e "$(BLUE)Rolling back migrations...$(NC)"
	@$(PYTHON_BIN) -m alembic downgrade -1

migration: ## Create new migration (use NAME=name)
	@echo -e "$(BLUE)Creating migration...$(NC)"
	@$(PYTHON_BIN) -m alembic revision --autogenerate -m "$(NAME)"

db-shell: ## Open database shell
	@echo -e "$(BLUE)Opening database shell...$(NC)"
	@psql $${DATABASE_URL}

## Docker
docker-build: ## Build Docker image
	@echo -e "$(BLUE)Building Docker image...$(NC)"
	docker builder build -t $(DOCKER_IMAGE) .

docker-infra: ## Start Docker infrastructure containers (DB, Qdrant)
	@echo -e "$(BLUE)Starting Docker infrastructure...$(NC)"
	docker compose --profile infra up -d

docker-prod: ## Start full Docker production stack
	@echo -e "$(BLUE)Starting full Docker production stack...$(NC)"
	docker compose --profile prod up -d

docker-down: ## Stop Docker containers
	@echo -e "$(BLUE)Stopping Docker containers...$(NC)"
	docker compose --profile prod down

docker-logs: ## Show Docker logs
	docker compose logs -f

## Utilities
clean: ## Clean up generated files
	@echo -e "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf build/ dist/ *.egg-info/ htmlcov/
	@rm -rf logs/*.log.*
	@rm -rf $(VENV)
	@rm -rf logs
	@echo -e "$(GREEN)✓ Cleanup complete$(NC)"

shell: ## Open Python shell with app context
	@echo -e "$(BLUE)Opening Python shell...$(NC)"
	@$(PYTHON_BIN) -i -c "from app.main import app; from app.core.config import settings; print('App loaded!')"

logs: ## Show application logs
	@tail -f logs/app.log 2>/dev/null || echo -e "$(YELLOW)No log file found$(NC)"

update: ## Update dependencies
	@echo -e "$(BLUE)Updating dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install --upgrade -r requirements.txt
	@echo -e "$(GREEN)✓ Dependencies updated$(NC)"

freeze: ## Freeze current dependencies
	@echo -e "$(BLUE)Freezing dependencies...$(NC)"
	@$(PIP) freeze > requirements.txt
	@echo -e "$(GREEN)✓ Dependencies frozen$(NC)"

list: ## List installed dependencies
	@echo -e "$(BLUE)Listing installed dependencies...$(NC)"
	@$(PIP) list

outdated: ## Check for outdated dependencies
	@echo -e "$(BLUE)Checking for outdated dependencies...$(NC)"
	@$(PIP) list --outdated

## CI/CD
ci: lint type-check ## Run CI pipeline checks
	@echo -e "$(GREEN)✓ CI checks passed$(NC)"

## Info
info: ## Show project information
	@echo -e "$(BLUE)Project Information:$(NC)"
	@echo -e "  Name: EcoRoute Atlas"
	@echo -e "  Python: $(shell python --version)"
	@echo -e "  Environment: $${ENVIRONMENT:-development}"
	@echo -e "  Database: $${DATABASE_URL:-postgresql://localhost:5432/ecoroute}"
	@echo -e "  Qdrant: $${QDRANT_HOST:-localhost}:$${QDRANT_PORT:-6333}"

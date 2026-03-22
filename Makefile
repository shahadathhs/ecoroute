.PHONY: help install run dev lint format clean migrate-up migrate-down shell db-shell

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
PIP := pip
VENV := ecoroute_venv
ACTIVATE := $(VENV)/bin/activate
PYTHON_BIN := $(VENV)/bin/python

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)EcoRoute Atlas - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

## Development Setup
install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo "$(YELLOW)Activate with: source $(ACTIVATE)$(NC)"

setup: venv install ## Full setup (venv + install)
	@echo "$(GREEN)✓ Setup complete! Activate with: source $(ACTIVATE)$(NC)"

## Running the Application
run: ## Run the application
	@echo "$(BLUE)Starting application...$(NC)"
	@$(PYTHON) run.py

dev: ## Run in development mode with hot reload
	@echo "$(BLUE)Starting development server...$(NC)"
	@$(PYTHON_BIN) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-verbose: ## Run in development mode with verbose logging
	@echo "$(BLUE)Starting development server (verbose)...$(NC)"
	@$(PYTHON_BIN) -m uvicorn app.main:app --reload --log-level debug

## Code Quality
lint: ## Run linter (ruff)
	@echo "$(BLUE)Linting code...$(NC)"
	@$(PYTHON_BIN) -m ruff check app/

lint-fix: ## Fix linting issues automatically
	@echo "$(BLUE)Fixing linting issues...$(NC)"
	@$(PYTHON_BIN) -m ruff check --fix app/

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(PYTHON_BIN) -m black app/

format-check: ## Check if code needs formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	@$(PYTHON_BIN) -m black --check app/

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Running type checks...$(NC)"
	@$(PYTHON_BIN) -m mypy app/

check-all: lint type-check ## Run all quality checks
	@echo "$(GREEN)✓ All checks passed$(NC)"

fix-all: lint-fix format ## Fix all auto-fixable issues
	@echo "$(GREEN)✓ Code fixed$(NC)"

## Database
migrate-up: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	@$(PYTHON_BIN) -m alembic upgrade head

migrate-down: ## Rollback database migrations
	@echo "$(BLUE)Rolling back migrations...$(NC)"
	@$(PYTHON_BIN) -m alembic downgrade -1

migration: ## Create new migration (use NAME=name)
	@echo "$(BLUE)Creating migration...$(NC)"
	@$(PYTHON_BIN) -m alembic revision --autogenerate -m "$(NAME)"

db-shell: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	@psql $${DATABASE_URL}

## Docker
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t ecoroute:latest .

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker compose up -d

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker compose down

docker-logs: ## Show Docker logs
	docker compose logs -f

## Utilities
clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@rm -rf .mypy_cache/ .ruff_cache/
	@rm -rf logs/*.log.*
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

shell: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@$(PYTHON_BIN) -i -c "from app.main import app; from app.core.config import settings; print('App loaded!')"

logs: ## Show application logs
	@tail -f logs/app.log 2>/dev/null || echo "$(YELLOW)No log file found$(NC)"

deps-update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	@$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

freeze: ## Freeze current dependencies
	@echo "$(BLUE)Freezing dependencies...$(NC)"
	@$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ Dependencies frozen$(NC)"

## CI/CD
ci: lint type-check ## Run CI pipeline checks
	@echo "$(GREEN)✓ CI checks passed$(NC)"

## Info
info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Name: EcoRoute Atlas"
	@echo "  Python: $(shell python --version)"
	@echo "  Environment: $${ENVIRONMENT:-development}"
	@echo "  Database: $${DATABASE_URL:-postgresql://localhost:5432/ecoroute}"
	@echo "  Qdrant: $${QDRANT_HOST:-localhost}:$${QDRANT_PORT:-6333}"

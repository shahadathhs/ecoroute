# EcoRoute Atlas

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![semantic-release: python](https://img.shields.io/badge/semantic--release-python-e10079.svg)](https://github.com/python-semantic-release/python-semantic-release)

![Alt](https://repobeats.axiom.co/api/embed/ca0dcdfe1dbf4b738ba57fd0aee7ab1b0fceef1a.svg "Repobeats analytics image")

## Table of Contents

- [Overview](#-overview)
- [Features](#-core-modules)
- [Architecture](#-technical-architecture)
- [Documentation](#-documentation)
- [Quick Start](#-local-development-setup)
- [Automated Releases](#-automated-releases)
- [Available Commands](#-available-make-commands)
- [Development Workflow](#-development-workflow)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## Overview

**EcoRoute Atlas** is a production-grade, AI-driven backend system for global supply chain management, sustainability tracking, and regulatory compliance. Built exclusively with **Python and FastAPI**, it integrates advanced AI (Atlas) to provide proactive decision support, automated regulatory audits, and carbon footprint optimization.

---

## 🌟 Core Modules
- **Identity & Access Management (IAM)**: Advanced RBAC with multi-tenancy support for global logistics organizations.
- **Intelligent Compliance (Atlas AI)**: LLM-powered regulatory assistant using RAG (Retrieval-Augmented Generation) for real-time legal audits.
- **Dynamic Sustainability Tracking**: Automated CO2 footprint calculation based on route telemetry and vehicle health.
- **Fleet & Asset Monitoring**: High-frequency IoT data ingestion for real-time diagnostics and proactive maintenance.

---

## 🏗️ Technical Architecture
The system is designed as a high-performance **FastAPI** application with a focus on asynchronous processing and modularity.

- **Stack**: Python 3.14+, FastAPI, Pydantic (v2), SQLAlchemy/asyncpg.
- **Data Layer**:
  - **PostgreSQL**: Primary store for structured shipments, assets, and user data.
  - **Qdrant**: High-dimensional vector database for Atlas AI's knowledge retrieval.
- **AI/LLM**: Integrates with OpenAI/Anthropic or local models (BGE/E5) for embeddings and inference.

---

## 🚀 API & RBAC Specification
The system implements a detailed Role-Based Access Control model across 7 distinct user roles:
- `Super Admin`, `Company Admin`, `Logistics Manager`, `Compliance Officer`, `Sustainability Lead`, `Standard Dispatcher`, `Driver`.

For the full production-grade endpoint specification, see the [API & RBAC Spec](./docs/API_RBAC_SPEC.md).

---

## 📚 Documentation
- [AI System Architecture (ATLAS.md)](./docs/ATLAS.md)
- [Vector Flow Documentation (ATLAS_INTEL_FLOW.md)](./docs/ATLAS_INTEL_FLOW.md)
- [Production Architecture (ECOROUTE_ARCHITECTURE.md)](./docs/ECOROUTE_ARCHITECTURE.md)
- [Business Requirements (ECOROUTE_BUSINESS_REQUIREMENTS.md)](./docs/ECOROUTE_BUSINESS_REQUIREMENTS.md)
- [Detailed API Specification (API_RBAC_SPEC.md)](./docs/API_RBAC_SPEC.md)
- [API Response Standard (API_RESPONSE_STANDARD.md)](./docs/API_RESPONSE_STANDARD.md)

---

## 🛠️ Local Development Setup

This project uses **uv** for fast package management and **Docker** for infrastructure services.

### Prerequisites

- **Python 3.14+** (project uses modern Python features)
- **Docker & Docker Compose** (for PostgreSQL and Qdrant)
- **uv** (fast Python package manager)

### Step 1: Install uv

If you don't have uv installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/shahadathhs/ecoroute.git
cd ecoroute

# Run full setup (creates venv + installs dependencies)
make setup
```

**What `make setup` does:**
- Creates `.venv` virtual environment using uv
- Installs all dependencies from `pyproject.toml`
- Sets up pre-commit hooks for code quality
- Downloads and installs all packages in seconds

### Step 3: Start Infrastructure Services

Start PostgreSQL and Qdrant in Docker:
```bash
make docker-infra
```

**This starts:**
- **PostgreSQL** on `localhost:5432` (user/pass: `postgres/postgres`, db: `ecoroute`)
- **Qdrant** on `localhost:6333` (vector database for Atlas AI)

**Why this approach?**
- Your FastAPI app runs locally with hot reload for fast development
- Infrastructure services run in Docker for consistency
- Single `.env` file works for both (compose.yaml auto-overrides URLs for Docker)

### Step 4: Run the Application

```bash
make dev
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔄 Automated Releases

This project uses **python-semantic-release** for fully automated versioning and releases. No manual version bumping required!

### How It Works

1. **Make commits** using [Conventional Commits](#conventional-commits) format
2. **Push to main** branch
3. **GitHub Actions** automatically:
   - Determines version bump based on commits
   - Updates version in code
   - Generates changelog
   - Creates git tag
   - Creates GitHub release
   - Uploads distribution files

### Conventional Commits

Your commit messages determine the version bump:

```bash
# Feature → Minor version bump (1.0.0 → 1.1.0)
git commit -m "feat: add user authentication"

# Bug fix → Patch version bump (1.0.0 → 1.0.1)
git commit -m "fix: resolve database connection issue"

# Breaking change → Major version bump (1.0.0 → 2.0.0)
git commit -m "feat: redesign API architecture

BREAKING CHANGE: Remove deprecated endpoints"

# Other types (no version bump)
git commit -m "docs: update README"
git commit -m "chore: upgrade dependencies"
git commit -m "style: format code"
git commit -m "refactor: improve code structure"
git commit -m "test: add user tests"
git commit -m "ci: improve CI workflow"
```

### Release Commands

```bash
# Preview what version will be released (without releasing)
make release-dry-run

# Generate/update CHANGELOG.md only
make release-changelog

# Actually publish (automated via CI, not for manual use)
make release-publish
```

---

## 📋 Available Make Commands

```bash
# Setup
make setup              # Full setup (venv + install + pre-commit)
make venv               # Create virtual environment
make install            # Install dependencies
make reset-venv         # Force reset venv (fix permission issues)

# Running
make dev                # Development server with hot reload
make dev-verbose        # Development with verbose logging
make prod               # Production server (4 workers)

# Code Quality
make lint               # Run ruff linter
make lint-fix           # Auto-fix linting issues
make format             # Format code with black
make format-check       # Check if code needs formatting
make type-check         # Run mypy type checker
make check-all          # Run all quality checks
make fix-all            # Fix all auto-fixable issues

# Pre-commit Hooks
make pre-commit-install # Install git hooks (runs before commits)
make pre-commit-run     # Run all hooks manually
make pre-commit-update  # Update hooks to latest versions

# Release Automation
make release-dry-run    # Preview next release version
make release-changelog  # Generate CHANGELOG.md
make release-publish    # Publish release (used by CI)

# Database
make migrate-up         # Run database migrations
make migrate-down       # Rollback last migration
make migration NAME=add_users  # Create new migration
make db-shell           # Open PostgreSQL shell

# Docker
make docker-infra       # Start DB + Qdrant (development)
make docker-prod        # Start full stack (API + DB + Qdrant)
make docker-down        # Stop all Docker services
make docker-logs        # Show Docker logs

# Utilities
make clean              # Clean generated files, venv, caches
make shell              # Python shell with app context
make logs               # Tail application logs
make update             # Update all dependencies
make list               # List installed packages
make add PKG=requests   # Add new package
make add-dev PKG=pytest  # Add dev package
make remove PKG=requests # Remove package
make freeze             # Update lock file

# CI/CD
make ci                 # Run all CI pipeline checks locally
make security           # Run security scan (bandit)
make info               # Show project information
```

---

## 📝 Development Workflow

### 1. Feature Development

```bash
# Create a new branch
git checkout -b feature/new-feature

# Make changes
vim app/services/new_feature.py

# Run quality checks (pre-commit hooks run automatically)
make fix-all

# Commit with conventional format
git add .
git commit -m "feat: add new feature for user management"

# Push to main to trigger release
git push origin feature/new-feature
# Create PR, merge to main
# 🎉 Automatic release!
```

### 2. Bug Fix

```bash
# Fix the bug
vim app/services/bugfix.py

# Check with pre-commit
make pre-commit-run

# Commit
git commit -m "fix: resolve timeout issue in API calls"

# Push → Automatic patch release
git push
```

### 3. Environment Configuration

The `.env` file contains all configuration:
```bash
# Application
APP_NAME=EcoRoute Atlas
ENVIRONMENT=development
DEBUG=true

# Server
HOST=127.0.0.1
PORT=8000

# Database (points to localhost for local development)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ecoroute

# Qdrant (points to localhost for local development)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Security
SECRET_KEY=your-secret-key-change-in-production

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Note:** When running `make docker-prod`, Docker Compose automatically overrides `DATABASE_URL` and `QDRANT_HOST` to point to Docker services.

---

## 🔧 Troubleshooting

### Port already in use?
```bash
# Check what's using the port
lsof -i :8000
# Or use a different port
PORT=9000 make dev
```

### Docker containers not starting?
```bash
# Check Docker logs
make docker-logs

# Restart Docker services
make docker-down
make docker-infra
```

### Dependencies not installing?
```bash
# Clean and reinstall
make clean
make setup
```

### Pre-commit hooks not running?
```bash
# Reinstall hooks
make pre-commit-install

# Run manually to check
make pre-commit-run
```

### Want to preview next release?
```bash
make release-dry-run
# Shows: what version will be released and changelog
```

---

## 🏗️ Project Structure

```
ecoroute/
├── app/
│   ├── api/              # HTTP routes (thin layer)
│   ├── core/             # Config, logging, errors
│   ├── db/               # Database session management
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   └── main.py           # Application entry point
├── docs/                 # Documentation
├── tests/                # Test suite (future)
├── .github/workflows/    # CI/CD workflows
├── pyproject.toml        # Project config & dependencies
├── Makefile              # Development automation
└── README.md
```

---

## 🔐 Security

- ✅ Automated security scanning with Bandit
- ✅ Pre-commit hooks for code quality
- ✅ Type checking with mypy
- ✅ Linting and formatting enforcement
- ✅ Host configurable (default: localhost only)
- ✅ CORS configuration for API access

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

- 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md) for development setup
- 🔐 Review [SECURITY.md](SECURITY.md) for vulnerability reporting
- 📋 Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community guidelines

---

## 📞 Support

- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Open an issue with the "enhancement" label
- ❓ **Questions**: Use GitHub Discussions
- 🔐 **Security Issues**: Email security@ecoroute.com

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by the EcoRoute Team**


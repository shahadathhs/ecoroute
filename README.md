# EcoRoute Atlas

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

- **Stack**: Python 3.12+, FastAPI, Pydantic (v2), SQLAlchemy/asyncpg.
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
- Downloads and installs 61 packages in seconds

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

### Available Make Commands

```bash
# Setup
make setup              # Full setup (venv + install)
make venv               # Create virtual environment
make install            # Install dependencies

# Running
make dev                # Development server with hot reload
make dev-verbose        # Development with verbose logging
make prod               # Production server (4 workers)

# Code Quality
make lint               # Run ruff linter
make lint-fix           # Auto-fix linting issues
make format             # Format code with black
make type-check         # Run mypy type checker
make check-all          # Run all quality checks
make fix-all            # Fix all auto-fixable issues

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
make remove PKG=requests # Remove package
```

### Development Workflow

1. **Make changes** to your code
2. **Auto-reload** detects changes and restarts the server
3. **Check logs** in terminal or with `make logs`
4. **Run tests** (when implemented)
5. **Commit changes** with git

### Environment Configuration

The `.env` file contains all configuration:
```bash
# Database (points to localhost for local development)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ecoroute

# Qdrant (points to localhost for local development)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Security
SECRET_KEY=your-secret-key-change-in-production

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Note:** When running `make docker-prod`, Docker Compose automatically overrides `DATABASE_URL` and `QDRANT_HOST` to point to Docker services.

### Troubleshooting

**Port already in use?**
```bash
# Check what's using the port
lsof -i :8000
# Or use a different port
PORT=9000 make dev
```

**Docker containers not starting?**
```bash
# Check Docker logs
make docker-logs

# Restart Docker services
make docker-down
make docker-infra
```

**Dependencies not installing?**
```bash
# Clean and reinstall
make clean
make setup
```

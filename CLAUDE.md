# EcoRoute Atlas - AI Development Guide

**Version**: 1.0.0
**Last Updated**: 2026-04-05
**Framework**: FastAPI 0.135.3, Python 3.14+

---

## 🎯 Project Overview

EcoRoute Atlas is an AI-driven backend system for global supply chain management, sustainability tracking, and regulatory compliance. The system uses FastAPI with async PostgreSQL and Qdrant vector database for AI-powered intelligence.

### Core Architecture
- **API Layer**: FastAPI with Pydantic v2 for validation
- **Data Layer**: SQLAlchemy 2.0 with asyncpg for PostgreSQL
- **Vector DB**: Qdrant for RAG-based AI intelligence (Atlas)
- **Authentication**: JWT with role-based access control (RBAC)
- **Logging**: Loguru for structured logging
- **Config**: Pydantic Settings with .env support

### Technology Stack
```python
# Core Dependencies
fastapi==0.135.3          # Web framework
uvicorn[standard]==0.43.0 # ASGI server
pydantic==2.12.5          # Data validation
pydantic-settings==2.13.1 # Configuration management
sqlalchemy[asyncio]==2.0.49  # ORM
asyncpg==0.31.0           # Async PostgreSQL driver
alembic==1.18.4           # Database migrations
qdrant-client==1.17.1     # Vector database client
python-jose[cryptography]==3.5.0  # JWT handling
passlib[bcrypt]==1.7.4    # Password hashing
loguru==0.7.3             # Logging
httpx==0.28.1             # Async HTTP client

# Development Tools
ruff==0.15.9              # Linting and formatting
black==26.3.1             # Code formatting
mypy==1.20.0              # Type checking
```

---

## 🏗️ Project Structure

```
ecoroute/
├── app/
│   ├── api/              # API route handlers
│   │   ├── __init__.py
│   │   ├── root.py       # Root endpoints
│   │   ├── health.py     # Health check endpoints
│   │   └── docs.py       # Documentation endpoints
│   ├── core/             # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py     # Configuration settings
│   │   ├── errors.py     # Error handlers
│   │   ├── logger.py     # Logging setup
│   │   └── response.py   # Response models
│   ├── db/               # Database layer
│   │   ├── __init__.py
│   │   └── session.py    # Database session management
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
│   └── main.py           # Application entry point
├── docs/                 # Documentation
├── tests/                # Test suite (future)
├── pyproject.toml        # Project configuration
├── Makefile              # Development automation
├── compose.yaml          # Docker compose setup
└── Dockerfile            # Production container image
```

---

## 🔧 Development Workflow

### Initial Setup
```bash
# Clone and setup
git clone https://github.com/shahadathhs/ecoroute.git
cd ecoroute
make setup              # Creates venv + installs dependencies
make pre-commit-install # Install git hooks (one-time)
```

### Daily Development
```bash
# Start infrastructure (PostgreSQL + Qdrant)
make docker-infra

# Run development server with hot reload
make dev                # http://localhost:8000
make dev-verbose        # With debug logging

# Run code quality checks
make lint               # Ruff linting
make type-check         # MyPy type checking
make format             # Black formatting
make check-all          # All quality checks
make fix-all            # Auto-fix issues

# Database operations
make migrate-up         # Run migrations
make migration NAME=add_users  # Create migration
make db-shell           # PostgreSQL shell
```

### Code Quality Standards
```bash
# Before committing
make fix-all            # Fix formatting and linting
make check-all          # Verify all checks pass

# Git hooks (pre-commit) run automatically
make pre-commit-run     # Run manually if needed
```

### Docker Operations
```bash
make docker-infra       # Start DB + Qdrant only
make docker-prod        # Start full stack (API + DB + Qdrant)
make docker-down        # Stop all services
make docker-logs        # View logs
```

---

## 📝 Code Conventions

### File Organization
- **Routes**: `app/api/` - One module per feature/endpoint group
- **Models**: `app/models/` - SQLAlchemy ORM models
- **Schemas**: `app/schemas/` - Pydantic request/response models
- **Services**: `app/services/` - Business logic layer
- **Core**: `app/core/` - Shared utilities (config, errors, logging)

### Naming Conventions
```python
# Files and modules: snake_case
user_service.py
database_session.py

# Classes: PascalCase
class UserService:
    class DatabaseSession:

# Functions and variables: snake_case
def get_user_by_id():
    user_id = 123

# Constants: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30

# Private: leading underscore
def _internal_helper():
    _private_var = "internal"
```

### Type Hints
```python
# Always include type hints
from typing import List, Optional
from app.models import User
from app.schemas import UserCreate

async def create_user(
    user_data: UserCreate,
    db: AsyncSession
) -> User:
    """Create a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user instance
    """
    pass
```

### Error Handling
```python
# Use custom exceptions
from app.core.errors import AppException

# Raise domain-specific exceptions
if not user:
    raise AppException(
        status_code=404,
        message="User not found",
        details={"user_id": user_id}
    )

# Log errors appropriately
from app.core.logger import logger
logger.error(f"Failed to create user: {e}", exc_info=True)
```

### Async Patterns
```python
# Always use async/await for I/O operations
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# Use async context managers
async with db.begin():
    # Database operations
    pass
```

---

## 🏛️ Architecture Patterns

### Dependency Injection
```python
# FastAPI Depends for dependencies
from fastapi import Depends
from app.db.session import get_db

@router.get("/users/{user_id}")
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)
    return user
```

### Configuration Management
```python
# Use settings from app.core.config
from app.core.config import settings

# Access configuration
database_url = settings.database_url
debug_mode = settings.debug
api_version = settings.app_version

# Environment-aware behavior
if settings.is_dev:
    logger.info("Development mode")
```

### Response Formatting
```python
# Use standardized response format
from app.core.response import success_response, error_response

@router.post("/users")
async def create_user_endpoint(user_data: UserCreate):
    try:
        user = await create_user(user_data)
        return success_response(
            data=user,
            message="User created successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(
            message="Failed to create user",
            details=str(e)
        )
```

### Database Operations
```python
# Use SQLAlchemy 2.0 async patterns
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

# Transactions
async def create_user_with_profile(
    db: AsyncSession,
    user_data: UserCreate
) -> User:
    async with db.begin():
        user = User(**user_data.dict())
        db.add(user)
        await db.flush()  # Get ID without committing

        profile = UserProfile(user_id=user.id)
        db.add(profile)

    return user
```

---

## 🧪 Testing Guidelines (Future)

### Test Organization
```python
# Test structure mirrors app structure
tests/
├── api/              # API endpoint tests
│   ├── test_users.py
│   └── test_auth.py
├── services/         # Service layer tests
│   └── test_user_service.py
├── models/           # Model tests
│   └── test_user_model.py
└── conftest.py       # Pytest configuration
```

### Test Patterns
```python
# Use pytest with async support
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/users",
            json={"email": "test@example.com"}
        )
    assert response.status_code == 201
```

---

## 🚀 Deployment Considerations

### Environment Variables
```bash
# Required environment variables
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
QDRANT_HOST=qdrant
QDRANT_PORT=6333
SECRET_KEY=your-secret-key
ENVIRONMENT=production
DEBUG=false
```

### Production Checklist
- [ ] Set `DEBUG=false` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up proper CORS origins
- [ ] Configure log aggregation
- [ ] Enable health checks
- [ ] Set up monitoring/alerting
- [ ] Run database migrations
- [ ] Use production ASGI server (uvicorn with workers)

### Docker Production
```bash
# Build production image
make docker-build

# Run full production stack
make docker-prod

# Or using docker compose directly
docker compose --profile prod up -d
```

---

## 📚 Documentation Standards

### Docstring Format
```python
def complex_function(param1: str, param2: int) -> dict:
    """Brief description of function.

    Longer description if needed. Explain the why, not just the what.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is invalid

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### API Documentation
- Use FastAPI's automatic OpenAPI docs
- Add detailed descriptions to endpoints
- Include request/response examples
- Document authentication requirements
- Tag endpoints by feature/domain

---

## 🔄 Migration Patterns

### Creating Migrations
```bash
# Generate migration from model changes
make migration NAME=add_user_preferences

# Review generated migration
# Edit if necessary to add custom logic

# Apply migration
make migrate-up

# Rollback if needed
make migrate-down
```

### Migration Best Practices
- Always review auto-generated migrations
- Use descriptive migration names
- Add data migrations in separate steps
- Test migrations on staging first
- Keep migrations reversible when possible

---

## 🎯 Common Tasks

### Adding a New Endpoint
1. Create route handler in `app/api/`
2. Create Pydantic schemas in `app/schemas/`
3. Create service logic in `app/services/`
4. Add routes to `app/main.py`
5. Add tests in `tests/api/`
6. Update API documentation

### Adding a New Model
1. Create SQLAlchemy model in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Generate migration: `make migration NAME=add_model_name`
4. Apply migration: `make migrate-up`
5. Add CRUD operations in `app/services/`

### Updating Dependencies
```bash
# Add new dependency
make add PKG=package-name

# Update all dependencies
make update

# Update lock file
make freeze

# Remove dependency
make remove PKG=package-name
```

---

## 🐛 Debugging Tips

### Enable Debug Logging
```bash
# Run with debug logging
make dev-verbose

# Or set environment variable
export LOG_LEVEL=DEBUG
make dev
```

### Database Issues
```bash
# Check database connection
make db-shell

# View migration status
python -m alembic current

# Rollback migration
make migrate-down
```

### Docker Issues
```bash
# View container logs
make docker-logs

# Restart infrastructure
make docker-down
make docker-infra

# Clean rebuild
docker compose down -v
docker compose --profile infra up -d --build
```

---

## 📋 Pre-Commit Checklist

Before committing code, ensure:
- [ ] All tests pass (`make test` - when implemented)
- [ ] Code formatted with black (`make format`)
- [ ] No linting errors (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] New features include tests
- [ ] Documentation updated
- [ ] Migrations created if models changed
- [ ] Environment variables documented

---

## 🔐 Security Considerations

### Authentication
- JWT tokens for API authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Token expiration and refresh

### Data Validation
- Pydantic schemas for all inputs
- SQL injection prevention (ORM parameterization)
- XSS prevention (FastAPI automatic escaping)
- CORS configuration for frontend access

### Secrets Management
- Never commit `.env` files
- Use environment variables for secrets
- Rotate secrets regularly
- Use different secrets for dev/prod

---

## 📞 Support and Contribution

### Getting Help
- Check existing documentation in `docs/`
- Review existing code patterns
- Run `make help` for available commands
- Check logs with `make logs`

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes following conventions
4. Run `make check-all` before committing
5. Submit a pull request with description

### Code Review Focus
- Adherence to code conventions
- Test coverage
- Documentation completeness
- Security considerations
- Performance implications

---

## 🎓 Learning Resources

### FastAPI Best Practices
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)

### Project-Specific
- API & RBAC Spec: `docs/API_RBAC_SPEC.md`
- AI Architecture: `docs/ATLAS.md`
- System Architecture: `docs/ECOROUTE_ARCHITECTURE.md`
- Business Requirements: `docs/ECOROUTE_BUSINESS_REQUIREMENTS.md`

---

**Note**: This document is a living guide. Update it as the project evolves and new patterns emerge.

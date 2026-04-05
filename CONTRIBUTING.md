# Contributing to EcoRoute Atlas

Thank you for your interest in contributing to EcoRoute Atlas! We welcome contributions from the community.

## Getting Started

### Prerequisites

- Python 3.14+
- Docker & Docker Compose
- uv (package manager)
- Familiarity with FastAPI, SQLAlchemy, and async Python

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/shahadathhs/ecoroute.git
cd ecoroute

# Setup development environment
make setup

# Start infrastructure services
make docker-infra

# Run development server
make dev
```

## Development Workflow

### 1. Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) to automate releases:

```bash
# Features (trigger minor version bump)
git commit -m "feat: add user authentication"

# Bug fixes (trigger patch version bump)
git commit -m "fix: resolve database timeout"

# Documentation (no version bump)
git commit -m "docs: update API documentation"

# Other types
chore:    # Maintenance tasks
style:     # Code formatting
refactor:  # Code restructuring
perf:      # Performance improvements
test:      # Adding tests
ci:        # CI/CD changes
```

### 2. Code Quality

Before committing, ensure code quality:

```bash
# Run all quality checks
make fix-all

# Run pre-commit hooks manually
make pre-commit-run

# Run CI pipeline locally
make ci
```

### 3. Branching Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git commit -m "feat: add your feature"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

## Project Structure

```
ecoroute/
├── app/
│   ├── api/           # HTTP routes
│   ├── core/          # Config, logging, errors
│   ├── db/            # Database session
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   └── services/      # Business logic
├── docs/              # Documentation
└── tests/             # Tests
```

### What Goes Where?

- **`app/api/`** - Route handlers (thin layer, just HTTP concerns)
- **`app/services/`** - Business logic and reusable functions
- **`app/models/`** - Database models (SQLAlchemy)
- **`app/schemas/`** - Request/response schemas (Pydantic)
- **`app/core/`** - Shared utilities (config, logger, errors)

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for classes, functions, and modules
- Keep functions under 50 lines when possible
- Keep files under 200 lines

### Example

```python
"""
User service module.
"""
from typing import Optional
from app.models import User
from app.schemas import UserCreate


class UserService:
    """Service for user-related operations."""

    async def create_user(self, data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            data: User creation data

        Returns:
            Created user instance
        """
        user = User(**data.model_dump())
        # ... business logic
        return user
```

### API Response Format

All API responses must follow the standard format:

```python
from app.core.response import ResponseBuilder

# Success response
return ResponseBuilder.success(
    data=user_data,
    message="User created successfully"
)

# Error response
return ResponseBuilder.not_found(
    message="User not found"
)
```

## Testing (Coming Soon)

We're working on a comprehensive test suite. For now:
- Write manual test cases for new features
- Test endpoints via Swagger UI at `/docs`
- Test database operations with `make db-shell`

## Pull Request Guidelines

### PR Title

Use conventional commit format:
```
feat: add user authentication
fix: resolve database connection issue
docs: update README
```

### PR Description

Include:
- **Why**: What problem does this solve?
- **What**: What changes were made?
- **How**: How was it implemented?
- **Testing**: How was it tested?
- **Screenshots**: For UI changes (if applicable)

### Checklist

- [ ] Code follows project style guidelines
- [ ] Ran `make fix-all` before committing
- [ ] Self-reviewed the code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings generated
- [ ] Added tests (when applicable)
- [ ] All tests pass (when implemented)

## Questions?

Feel free to open an issue with the question label or contact maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

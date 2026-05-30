# FastAPI + SQLAlchemy Backend

## Overview
Async Python backend with FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic.

## Tech Stack
Framework: FastAPI
Database: PostgreSQL via SQLAlchemy 2.0 async (async session)
Migrations: Alembic
Validation: Pydantic v2
Auth: JWT (python-jose) + OAuth2
Testing: pytest + httpx
Language: Python 3.12+

## Architecture
- app/api/      Route handlers (versioned v1/, v2/)
- app/core/     Config, security, dependencies
- app/models/   SQLAlchemy ORM models
- app/schemas/  Pydantic request/response schemas
- app/services/ Business logic layer
- tests/        pytest test suite
- alembic/      Database migrations

## Code Rules
- Async endpoints by default
- Pydantic v2 for all validation
- Service layer between routes and DB
- Dependency injection for auth, DB sessions
- Type hints everywhere (mypy strict mode)

## Common Tasks

### New Endpoint
1. Schema in schemas/
2. Service function in services/
3. Route handler in api/v1/
4. Tests in tests/api/

### New DB Model
1. Model in models/
2. alembic revision --autogenerate -m "desc"
3. alembic upgrade head
4. Update Pydantic schema

## Commands
- uvicorn app.main:app --reload   Dev server
- pytest                           Run tests
- pytest --cov=app                 Coverage report
- alembic upgrade head             Run migrations
- mypy app                         Type checking
- ruff check .                     Linting and formatting
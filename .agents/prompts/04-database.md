# Database Module — Production Implementation Prompt

## Objective

Implement the complete production-ready Database Module for Tailr.

This module is the foundation of persistence, transactions, repositories, migrations, health checks, and dependency injection.

The implementation must follow:

- Hexagonal Architecture
- Domain Driven Design (DDD)
- Async-first design
- SQLAlchemy 2.x
- PostgreSQL 18
- Pydantic v2
- Structured logging
- OpenTelemetry-ready observability

---

## Read First

Before generating code, read:

- `.agents/AGENTS.md`
- `.agents/workflow.md`
- `.agents/architecture.md`
- `.agents/coding-standards.md`
- `.agents/rules/architecture.md`
- `.agents/rules/python.md`
- `.agents/rules/database.md`
- `.agents/rules/testing.md`
- `.agents/rules/logging.md`
- `.agents/rules/security.md`

Do not generate code until these documents are understood.

---

## Architecture Constraints

### Never expose ORM models

ORM models are infrastructure-only.

Allowed:

- Repository returns domain entities
- Repository returns DTOs
- Repository returns Pydantic schemas

Forbidden:

- Returning SQLAlchemy ORM models from services
- Returning ORM models from API routes
- Passing ORM models into the domain layer

---

## Required Folder Structure

Implement the following structure exactly:

```text
backend/
├── infrastructure/
│   └── database/
│       ├── __init__.py
│       ├── base.py
│       ├── engine.py
│       ├── session.py
│       ├── health.py
│       ├── transaction.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── resume_repository.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── mixins.py
│       │   ├── system_info.py
│       │   └── guardrail_audit.py
│       └── migrations/
│
├── dependencies/
│   └── database.py
│
└── tests/
    ├── unit/
    └── integration/
```

---

## Implement

### Async SQLAlchemy

Create an async engine using:

- `create_async_engine`
- `asyncpg`
- pool sizing
- pool recycle
- pool pre-ping
- echo configurable from settings

---

### Session Factory

Provide:

- `AsyncSessionLocal`
- `get_db()` dependency
- context-managed sessions
- automatic rollback on failure
- automatic session cleanup

---

### Base Model

Implement a declarative base that supports:

- UUID primary keys (UUIDv7 preferred, UUID4 acceptable)
- created_at
- updated_at
- deleted_at
- soft delete
- version field (optimistic locking)

---

### Mixins

Implement reusable mixins:

- `UUIDMixin`
- `TimestampMixin`
- `SoftDeleteMixin`
- `VersionMixin`

These must be composable and independently testable.

---

### Transactions

Implement a transaction manager that supports:

- nested transactions
- rollback on exception
- async context manager
- explicit transaction boundaries
- integration with application services

Example:

```python
async with transaction_manager.transaction():
    ...
```

---

### Repositories

Implement a generic async repository base class with:

- get_by_id
- get_all
- create
- update
- delete (soft delete)
- exists
- paginate
- count

Then implement a sample `ResumeRepository`.

Repositories must:

- accept `AsyncSession`
- return domain entities
- never commit automatically
- never contain business logic

---

### Alembic

Generate a production-ready Alembic setup with:

- env.py
- async migration support
- naming conventions
- metadata discovery
- migration script template

Generate an initial migration containing:

- system_info
- guardrail_audit

---

### Connection Pooling

Configure:

- pool_size
- max_overflow
- pool_timeout
- pool_recycle
- pool_pre_ping

Values must come from settings.

---

### Health Checks

Implement database health checks that verify:

- connectivity
- ability to execute a simple query
- connection pool status
- latency measurement

Expose a function:

```python
async def check_database_health() -> HealthStatus
```

---

### Dependency Injection

Create FastAPI dependencies:

```python
get_db()
get_transaction_manager()
get_resume_repository()
```

Dependencies must be async and type-safe.

---

### Guardrail Audit Table

Implement a table for guardrail events.

Fields:

- id
- request_id
- validator
- status
- violations
- repaired
- metadata (JSONB)
- created_at

Use JSONB for structured audit data.

---

### Structured Logging

Use the telemetry package.

Log:

- engine startup
- connection failures
- transaction begin/commit/rollback
- migration execution
- slow queries (> configurable threshold)

Never log credentials.

---

## Testing Requirements

Generate:

### Unit Tests

- mixins
- transaction manager
- repository base
- health check logic

### Integration Tests

- PostgreSQL connection
- CRUD operations
- soft delete behavior
- rollback behavior
- migration execution

Use:

- pytest
- pytest-asyncio
- testcontainers (preferred)
- async fixtures

Target coverage: **90%+** for database modules.

---

## Documentation

Generate:

### `README.md`

Include:

- architecture overview
- setup instructions
- migration commands
- repository usage examples
- transaction examples
- health check examples

### Migration Commands

Document:

```bash
alembic revision --autogenerate -m "..."
alembic upgrade head
alembic downgrade -1
```

---

## Acceptance Criteria

The module is complete only if:

- Async engine works
- Sessions are properly cleaned up
- Transactions rollback correctly
- Repositories are generic and reusable
- ORM models never leave infrastructure
- Alembic migrations run successfully
- Health checks return structured results
- Tests pass
- Ruff passes
- MyPy passes
- Documentation is generated
- No TODOs remain
- No placeholder implementations remain

---

## Output Format

Return:

1. Complete file tree
2. Full source code for every file
3. Alembic migration files
4. Test files
5. README.md
6. Example usage snippets
7. Commands to run locally
8. Any architectural trade-offs made

Do not return partial implementations.

Do not return pseudo-code.

Do not omit imports.

Generate production-ready code only.

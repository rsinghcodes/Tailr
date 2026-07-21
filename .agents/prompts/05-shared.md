# Shared Foundation — Production Implementation Prompt

## Objective

Implement the complete production-ready **Shared Foundation module** for Tailr.

This module provides reusable building blocks that can be used across all layers of the system:

- API Layer
- Application Layer
- Domain Layer
- Infrastructure Layer
- AI Agents
- Workflows
- Guardrails

The Shared Foundation must contain **no business logic**.

Everything must be framework-agnostic where possible and independently testable.

---

## Read First

Before generating code, read:

- `.agents/AGENTS.md`
- `.agents/workflow.md`
- `.agents/architecture.md`
- `.agents/coding-standards.md`
- `.agents/rules/architecture.md`
- `.agents/rules/python.md`
- `.agents/rules/testing.md`
- `.agents/rules/logging.md`
- `.agents/rules/security.md`

Do not generate code until these documents are understood.

---

## Architecture Constraints

### Shared Foundation must remain generic

Allowed:

- Exceptions
- Enums
- Response models
- Pagination utilities
- Generic validators
- Constants
- Type aliases
- Base classes
- Utility functions

Forbidden:

- Resume-specific logic
- Job-specific logic
- Database access
- FastAPI route handlers
- SQLAlchemy models
- LLM calls
- Qdrant access
- Redis access
- Workflow orchestration

If a component contains domain-specific behavior, it belongs in the Domain or Application layer.

---

## Required Folder Structure

Implement the following structure exactly:

```text
backend/
├── shared/
│   ├── __init__.py
│   │
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── validation.py
│   │   ├── authentication.py
│   │   ├── authorization.py
│   │   ├── database.py
│   │   ├── provider.py
│   │   ├── workflow.py
│   │   ├── guardrails.py
│   │   └── parsing.py
│   │
│   ├── enums/
│   │   ├── __init__.py
│   │   ├── status.py
│   │   ├── error_codes.py
│   │   ├── workflow.py
│   │   └── provider.py
│   │
│   ├── pagination/
│   │   ├── __init__.py
│   │   ├── params.py
│   │   ├── models.py
│   │   └── utils.py
│   │
│   ├── responses/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── success.py
│   │   ├── error.py
│   │   └── metadata.py
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── common.py
│   │   ├── files.py
│   │   └── strings.py
│   │
│   ├── constants/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── files.py
│   │   ├── limits.py
│   │   └── security.py
│   │
│   ├── types/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── pagination.py
│   │   ├── workflow.py
│   │   └── provider.py
│   │
│   ├── base/
│   │   ├── __init__.py
│   │   ├── entity.py
│   │   ├── value_object.py
│   │   ├── service.py
│   │   ├── event.py
│   │   └── validator.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── datetime.py
│   │   ├── uuid.py
│   │   ├── hashing.py
│   │   ├── serialization.py
│   │   ├── retry.py
│   │   └── text.py
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── health.py
│       ├── pagination.py
│       └── common.py
│
└── tests/
    ├── unit/
    └── integration/
```

---

## Implement

### Exceptions

Create a hierarchical exception system.

Base exception:

```python
ApplicationError
```

Derived exceptions:

- ValidationError
- AuthenticationError
- AuthorizationError
- DatabaseError
- ProviderError
- WorkflowError
- GuardrailError
- ParsingError

Requirements:

- error_code
- message
- details
- metadata
- HTTP status code mapping
- serializable representation

---

### Enums

Implement strongly typed enums using `StrEnum`.

Required enums:

- `StatusEnum`
- `WorkflowStatus`
- `ProviderType`
- `ErrorCode`

Error codes must include categories:

- VALIDATION\_\*
- AUTH\_\*
- DATABASE\_\*
- PROVIDER\_\*
- WORKFLOW\_\*
- GUARDRAIL\_\*
- PARSER\_\*
- SYSTEM\_\*

---

### Pagination

Implement reusable pagination.

Features:

- page
- page_size
- offset
- limit
- total
- total_pages
- has_next
- has_previous

Provide:

```python
PaginationParams
PaginatedResponse[T]
paginate_sequence()
calculate_pagination()
```

Maximum page size must be configurable.

---

### Standard API Responses

Implement a consistent API response format.

Success:

```json
{
  "success": true,
  "data": {},
  "meta": {}
}
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {}
  },
  "request_id": "..."
}
```

Support generics:

```python
SuccessResponse[T]
PaginatedSuccessResponse[T]
ErrorResponse
```

---

### Validation Framework

Create a lightweight reusable validation framework.

Base interface:

```python
class Validator(Protocol):
    def validate(self, value: Any) -> ValidationResult: ...
```

Implement validators for:

- email
- URL
- UUID
- file extension
- file size
- MIME type
- non-empty string
- length limits
- regex patterns

ValidationResult must contain:

- valid
- errors
- warnings
- normalized_value

---

### Constants

Centralize all shared constants.

Examples:

- API_VERSION
- DEFAULT_PAGE_SIZE
- MAX_PAGE_SIZE
- MAX_UPLOAD_SIZE
- ALLOWED_FILE_EXTENSIONS
- ALLOWED_MIME_TYPES
- REQUEST_ID_HEADER
- CORRELATION_ID_HEADER
- DEFAULT_TIMEOUT
- MAX_RETRY_ATTEMPTS

No magic numbers anywhere else in the codebase.

---

### Type Aliases

Create reusable type aliases.

Examples:

```python
RequestId
CorrelationId
UserId
ResumeId
WorkflowId
JSONDict
JSONValue
Metadata
Headers
QueryParams
```

Use `TypeAlias` syntax.

---

### Base Classes

Implement reusable abstract base classes.

#### Entity

- id
- equality by identity
- domain event support

#### ValueObject

- immutable
- equality by value

#### DomainService

- marker base class

#### DomainEvent

- event_id
- occurred_at
- aggregate_id

#### BaseValidator

- reusable validation helpers

These classes must not depend on infrastructure.

---

### Utility Functions

Implement production-ready utilities.

#### datetime.py

- utc_now()
- to_iso()
- parse_iso()
- ensure_utc()

#### uuid.py

- generate_uuid()
- generate_uuid_v7() (fallback to v4 if unavailable)

#### hashing.py

- sha256_hash()
- md5_hash() (for non-security use only)

#### serialization.py

- to_json()
- from_json()
- safe_json_dumps()

#### retry.py

- exponential_backoff()
- async_retry decorator

#### text.py

- normalize_whitespace()
- truncate_text()
- slugify()
- remove_control_characters()

---

### Common Schemas

Implement reusable Pydantic schemas.

- HealthResponse
- ErrorDetail
- RequestMetadata
- PaginationMeta
- TimestampedSchema

Use Pydantic v2 features:

- ConfigDict
- field validators
- computed fields
- strict mode

---

## Testing Requirements

Generate comprehensive tests.

### Unit Tests

- exception serialization
- enum values
- pagination calculations
- response models
- validators
- utility functions
- base class behavior

### Integration Tests

- response serialization
- validation pipeline
- pagination end-to-end

Target coverage: **95%+** for shared modules.

Use:

- pytest
- pytest-asyncio (if async utilities exist)
- parameterized tests
- property-based tests where useful

---

## Documentation

Generate:

### README.md

Include:

- module overview
- usage examples
- exception hierarchy
- pagination examples
- response examples
- validator examples
- utility examples

### API Response Examples

Document standard success and error responses.

### Exception Mapping Table

Map exceptions to HTTP status codes.

---

## Quality Requirements

The implementation must:

- be fully typed
- have no `Any` unless justified
- have no circular imports
- support Python 3.13
- be Ruff compliant
- be Black formatted
- be MyPy clean
- contain no TODOs
- contain no placeholder implementations

---

## Acceptance Criteria

The module is complete only if:

- all shared components are reusable
- no business logic exists
- exceptions serialize correctly
- pagination works correctly
- response models are generic
- validators are composable
- utilities are independently testable
- tests pass
- documentation is generated
- public APIs are stable

---

## Output Format

Return:

1. Complete file tree
2. Full source code for every file
3. Test files
4. README.md
5. Usage examples
6. Exception hierarchy diagram
7. API response examples
8. Architectural trade-offs

Do not return pseudo-code.

Do not omit imports.

Generate production-ready code only.

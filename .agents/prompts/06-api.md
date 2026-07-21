# API Layer — Production Implementation Prompt

## Objective

Implement the complete production-ready **API Layer** for Tailr.

This layer is responsible for:

- RESTful routing,
- request validation,
- response serialization,
- dependency injection,
- authentication and authorization,
- error handling,
- streaming support,
- health endpoints,
- rate limiting,
- OpenAPI documentation,
- and guardrail rejection responses.

The API layer must remain **HTTP-only** and contain **no business logic**.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/fastapi.md
- rules/security.md
- rules/testing.md
- rules/logging.md
- ADR-0002 — Clean Architecture
- ADR-0003 — Use FastAPI
- ADR-0011 — Validation & Guardrails Engine
- 11-API-Specification.md
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Architecture Constraints

## Allowed

- Routing
- Request validation
- Response serialization
- Dependency injection
- Authentication
- Authorization
- Exception-to-HTTP mapping

## Forbidden

- Database access
- SQL queries
- Prompt creation
- LLM calls
- Business rules
- Repository implementation
- Guardrail enforcement (guardrails run inside the application/workflow layer)
- Direct GuardrailsEngine instantiation

Routers never call validators, never inspect a `GuardrailResult`, and never decide what to do with a rejection.

They only translate whatever typed exception the Application layer raises into an HTTP response.

---

# Responsibilities

Implement the following API components.

---

## Router Organization

Create one router per domain:

- `resume.py` — resume CRUD and versioning
- `job.py` — job description analysis
- `knowledge.py` — knowledge indexing and search
- `workflow.py` — workflow orchestration
- `optimization.py` — rewrite plan, rewrite, validate
- `guardrails.py` — audit/read-only endpoints only
- `ats.py` — ATS analysis and comparison
- `render.py` — LaTeX generation and PDF compilation
- `analytics.py` — optimization history and dashboard
- `health.py` — liveness, readiness, startup probes
- `auth.py` — authentication endpoints

All routers are mounted under `/api/v1`.

---

## Request Validation

Use **Pydantic v2** with strict validation for all request models.

### Requirements

- typed request bodies,
- typed path parameters,
- typed query parameters,
- field-level validation with Pydantic validators,
- explicit error messages,
- and maximum request size enforcement.

---

## Response Models

Use standardized response format for all endpoints.

### Success Response

```json
{
  "success": true,
  "data": {},
  "meta": {},
  "request_id": "..."
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "details": []
  },
  "request_id": "..."
}
```

### Guardrail Rejection Response

```json
{
  "success": false,
  "error": {
    "code": "GUARDRAIL_REJECTED",
    "message": "AI output failed guardrail validation.",
    "details": {
      "violations": [],
      "affected_section": "..."
    }
  },
  "request_id": "..."
}
```

Support generics:

- `SuccessResponse[T]`
- `PaginatedSuccessResponse[T]`
- `ErrorResponse`

Never return ORM objects.

Never return AI-generated content in a response model unless the Application layer has already confirmed its `GuardrailResult.status` was `approved` or `repaired`.

---

## Authentication

Implement JWT Bearer Token authentication.

### Requirements

- token extraction from `Authorization` header,
- signature validation,
- expiration validation,
- issuer and audience validation,
- dependency injectable `get_current_user()`,
- and support for future OAuth2/OpenID Connect.

---

## Authorization

Implement resource-level authorization.

### Requirements

- verify resource ownership on every request,
- deny-by-default authorization,
- never trust frontend permissions,
- and typed permission checks.

---

## Dependency Injection

Use `Depends()` for all service injection.

### Expose Dependencies

- `get_current_user()`
- `get_db_session()`
- `get_resume_service()`
- `get_job_service()`
- `get_workflow_service()`
- `get_knowledge_service()`
- `get_ats_service()`
- `get_render_service()`
- `get_analytics_service()`

### Forbidden

- instantiating services inside routers,
- instantiating `GuardrailsEngine` or validators inside routers,
- and hidden dependency construction.

If a router needs guardrail outcomes (e.g., audit endpoint), inject the Application Service that already coordinates with Guardrails.

---

## Error Handling

Implement centralized exception handlers.

### Exception-to-HTTP Mapping

| Exception                   | Status | Error Code          |
| --------------------------- | ------ | ------------------- |
| ValidationError             | 422    | VALIDATION_ERROR    |
| AuthenticationError         | 401    | AUTH_ERROR          |
| AuthorizationError          | 403    | FORBIDDEN           |
| NotFoundError               | 404    | NOT_FOUND           |
| ConflictError               | 409    | CONFLICT            |
| GuardrailRejectionError     | 422    | GUARDRAIL_REJECTED  |
| ProviderError               | 502    | PROVIDER_ERROR      |
| WorkflowError               | 500    | WORKFLOW_ERROR      |
| RateLimitExceededError      | 429    | RATE_LIMITED        |
| ApplicationError (fallback) | 500    | INTERNAL_ERROR      |

A `GuardrailRejectionError` raised by the Application layer is caught by a dedicated exception handler and converted into a structured error response containing violation codes and affected section.

Never expose tracebacks.

A Guardrails rejection is never mapped to 500.

---

## Streaming

Use `StreamingResponse` for LLM-related endpoints.

### Requirements

- stream provider tokens internally for progress/UX,
- only emit actual resume content after the complete response has passed through Guardrails,
- if a rejection occurs after streaming has started, terminate with a structured error event,
- and never leave partial unvalidated content in the client buffer.

---

## Rate Limiting

Implement configurable rate limiting.

### Default Limits

| Endpoint Category  | Limit               |
| ------------------ | ------------------- |
| Default API        | 100 requests/minute |
| AI Endpoints       | 20 requests/minute  |
| Guardrails Audit   | 60 requests/minute  |
| File Uploads       | 10 uploads/minute   |

Limits are configurable per user and per IP.

---

## Pagination

All collection endpoints must support pagination.

### Parameters

- `page` (default: 1)
- `page_size` (default: 20, maximum: 100)
- `sort` (field name)
- `order` (asc/desc)

### Response Metadata

```json
{
  "page": 1,
  "page_size": 20,
  "total": 150,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false
}
```

---

## Health Endpoints

Expose:

- `/health/live` — application process status only
- `/health/ready` — verify PostgreSQL, Redis, Qdrant, LLM router, prompt registry, guardrails registry
- `/health/startup` — whether startup completed

### Requirements

- `/ready` must verify the Guardrails Engine's dependencies are loaded,
- a service that is "up" but cannot run Guardrails must not report ready,
- and no secrets or internal configuration values are exposed.

---

## Idempotency

Support `Idempotency-Key` header for workflow creation endpoints.

---

## OpenAPI Documentation

Every endpoint must be fully documented.

### Requirements

- descriptive summary and description,
- typed request/response schemas,
- guardrail rejection error shape documented for AI-facing endpoints,
- example request/response bodies,
- and proper status code documentation.

---

# Required File Structure

Generate production-ready files:

```text
api/
├── __init__.py
├── dependencies/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── services.py
│   └── pagination.py
├── middleware/
│   ├── __init__.py
│   └── rate_limit.py
├── routers/
│   ├── __init__.py
│   ├── resume.py
│   ├── job.py
│   ├── knowledge.py
│   ├── workflow.py
│   ├── optimization.py
│   ├── guardrails.py
│   ├── ats.py
│   ├── render.py
│   ├── analytics.py
│   ├── health.py
│   └── auth.py
├── schemas/
│   ├── __init__.py
│   ├── requests/
│   │   ├── resume.py
│   │   ├── job.py
│   │   ├── workflow.py
│   │   ├── optimization.py
│   │   ├── ats.py
│   │   └── render.py
│   └── responses/
│       ├── resume.py
│       ├── job.py
│       ├── workflow.py
│       ├── optimization.py
│       ├── guardrails.py
│       ├── ats.py
│       ├── render.py
│       ├── analytics.py
│       └── health.py
├── exceptions/
│   ├── __init__.py
│   └── handlers.py
└── docs/
    └── api.md
```

---

# Testing Requirements

Generate tests for:

- every router endpoint (success and failure paths),
- request validation (valid and invalid inputs),
- response model serialization,
- authentication (valid token, expired token, missing token),
- authorization (owner access, non-owner access),
- dependency injection wiring,
- exception handler mapping,
- guardrail rejection error responses,
- pagination (boundary values),
- rate limiting,
- health endpoints,
- streaming error termination,
- and OpenAPI schema generation.

Use:

- pytest
- pytest-asyncio
- httpx.AsyncClient
- mock Application Services (never mock business logic)

Tests must be deterministic.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings for all public functions,
- avoid global mutable state,
- be async-first,
- support dependency overrides in tests,
- and be production deployable.

### Additional Constraints

- no TODO placeholders,
- no tutorial code,
- no synchronous I/O,
- no business logic in routers,
- and no direct GuardrailsEngine calls from routers.

---

# Output Requirements

Return:

1. complete production-ready source files,
2. test files,
3. request/response schema examples,
4. exception mapping documentation,
5. rate limiting configuration,
6. authentication flow explanation,
7. pagination usage examples,
8. OpenAPI customization explanation,
9. streaming design explanation,
10. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready API layer** that provides:

- RESTful routing,
- strict validation,
- secure authentication,
- standardized responses,
- structured error handling,
- guardrail rejection transparency,
- streaming support,
- rate limiting,
- and comprehensive OpenAPI documentation

for the entire Tailr platform.

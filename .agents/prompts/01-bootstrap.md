# Bootstrap Module Prompt

## Objective

Implement the **application bootstrap layer** for Tailr.

This module is responsible for:

- creating the FastAPI application,
- wiring infrastructure dependencies,
- configuring telemetry,
- registering middleware,
- exposing operational endpoints,
- initializing guardrails,
- and validating runtime configuration.

The bootstrap layer must remain **framework-only** and contain **no business logic**.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- coding-standards.md
- rules/architecture.md
- rules/python.md
- rules/fastapi.md
- rules/security.md
- rules/testing.md
- ADR-0002 — Clean Architecture
- ADR-0003 — FastAPI
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0011 — Validation & Guardrails Engine
- 20-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Responsibilities

Implement the following bootstrap components.

---

## Application Factory

Create `create_app()` that:

- loads validated settings,
- configures OpenAPI metadata,
- registers exception handlers,
- registers middleware,
- registers API routers,
- configures lifespan management,
- and returns a fully initialized FastAPI instance.

### Requirements

- environment-aware configuration,
- typed settings,
- no global mutable application state,
- and deterministic startup behavior.

---

## Lifespan Management

Implement an async lifespan context that:

- runs startup orchestration,
- runs shutdown orchestration,
- handles graceful cancellation,
- cleans up resources,
- and logs lifecycle events.

### Requirements

- use `asynccontextmanager`,
- fail fast on startup errors,
- ensure partial startup cleanup,
- and support future background worker registration.

---

## Startup

Initialize the following infrastructure.

### Telemetry

- structured logging,
- OpenTelemetry tracing,
- Prometheus metrics,
- request/correlation ID propagation.

### Infrastructure

- PostgreSQL connection pool,
- Redis client,
- Qdrant client,
- HTTP client pool,
- object storage client (future-ready).

### AI Infrastructure

- LLM provider registry,
- prompt registry cache,
- guardrail registry,
- evaluation registry metadata,
- workflow engine registry.

### Startup Validation

Verify:

- database connectivity,
- Redis connectivity,
- Qdrant connectivity,
- LLM provider availability,
- prompt registry availability,
- and guardrail registry availability.

Startup must fail if any **critical dependency** is unavailable.

---

## Shutdown

Gracefully close:

- database engine,
- Redis connections,
- HTTP clients,
- telemetry exporters,
- workflow executors,
- background task managers,
- and any open file handles.

### Requirements

- no resource leaks,
- timeout-aware shutdown,
- idempotent cleanup,
- and structured shutdown logging.

---

## Middleware Registration

Register middleware in the following order:

```text
1. Request ID middleware
2. Correlation ID middleware
3. Structured logging middleware
4. Metrics middleware
5. Tracing middleware
6. Security headers middleware
7. CORS middleware
8. GZip middleware
9. Upload size limit middleware
10. Rate limiting middleware (future-ready)
```

Document the reason for the ordering.

---

## Dependency Injection

Use a **provider/container pattern**.

Expose providers for:

- settings,
- database session,
- Redis client,
- vector store,
- LLM router,
- prompt registry,
- guardrails engine,
- workflow engine,
- telemetry services,
- and storage services.

### Forbidden

- instantiating infrastructure inside routers,
- global singleton clients without lifecycle management,
- and hidden dependency construction.

---

## Configuration Loading

Use **Pydantic v2 BaseSettings**.

### Requirements

- typed configuration objects,
- environment variable validation,
- startup validation,
- environment-specific overrides,
- and secure default values.

### Supported Environments

- development
- testing
- staging
- production

Invalid configuration must stop application startup.

---

## Health Checks

Expose:

- `/health/live`
- `/health/ready`
- `/health/startup`

### Liveness

Returns application process status only.

### Readiness

Must verify:

- PostgreSQL,
- Redis,
- Qdrant,
- LLM router,
- prompt registry,
- and guardrails registry.

### Startup

Returns whether startup completed successfully.

### Response Format

```json
{
  "status": "ready",
  "checks": {
    "postgres": "ok",
    "redis": "ok",
    "qdrant": "ok",
    "llm": "ok",
    "guardrails": "ok"
  },
  "timestamp": "2026-07-20T10:00:00Z"
}
```

Do not expose secrets or internal configuration values.

---

# Telemetry Requirements

Configure:

- structured JSON logging,
- OpenTelemetry tracing,
- Prometheus metrics,
- request IDs,
- correlation IDs,
- trace propagation,
- and workflow-aware logging context.

Every request log must include:

- request_id,
- correlation_id,
- trace_id,
- span_id (when available),
- method,
- path,
- status_code,
- duration_ms,
- and client_ip.

No `print()` statements are allowed.

---

# Guardrails Requirements

Initialize the **Guardrails Engine registry** during startup.

Register validators:

- schema validator,
- JSON validator,
- hallucination detector,
- resume integrity validator,
- prompt injection detector,
- PII / secret scanner,
- ATS validator,
- LaTeX safety validator,
- and repair engine.

Load guardrail profiles from typed settings.

The bootstrap layer must ensure the registry is available before any AI workflow can start.

---

# Security Requirements

Enforce:

- secure CORS configuration,
- trusted host validation,
- HTTPS/HSTS in production,
- security headers,
- request size limits,
- upload size limits,
- exception sanitization,
- and no stack traces in production responses.

### Security Headers

- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy
- Strict-Transport-Security (production)

---

# Constraints

## Forbidden

- business logic,
- repositories,
- SQL queries,
- AI calls,
- prompt generation,
- workflow orchestration,
- domain entities,
- application services,
- and direct database mutations.

## Allowed

- framework wiring,
- dependency registration,
- infrastructure initialization,
- telemetry setup,
- health probes,
- middleware configuration,
- configuration validation,
- and lifecycle management.

---

# Required File Structure

Generate production-ready implementations for:

```text
app/
├── factory.py
├── lifespan.py
├── startup.py
├── shutdown.py
├── middleware/
│   ├── request_id.py
│   ├── correlation_id.py
│   ├── logging.py
│   ├── metrics.py
│   ├── tracing.py
│   ├── security_headers.py
│   └── upload_limits.py
├── dependencies/
│   ├── container.py
│   ├── database.py
│   ├── redis.py
│   ├── vector_store.py
│   ├── llm.py
│   ├── prompts.py
│   ├── guardrails.py
│   └── workflows.py
└── health/
    ├── live.py
    ├── ready.py
    └── startup.py
```

---

# Testing Requirements

Generate tests for:

- application factory,
- lifespan startup/shutdown,
- middleware registration order,
- request ID propagation,
- correlation ID propagation,
- security headers,
- configuration validation,
- health endpoints,
- dependency container wiring,
- startup failure scenarios,
- shutdown cleanup,
- and guardrails registry initialization.

Use:

- pytest,
- pytest-asyncio,
- httpx.AsyncClient,
- and Testcontainers where appropriate.

Do not mock business logic.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings for public functions,
- avoid global mutable state,
- be async-first,
- support graceful shutdown,
- support dependency overrides in tests,
- and be production deployable.

### Additional Requirements

- no TODO placeholders,
- no tutorial code,
- no synchronous I/O,
- and no hidden side effects during import.

---

# Required Deliverables

Return:

1. complete production-ready source files,
2. test files,
3. configuration examples (`.env.example`),
4. middleware ordering explanation,
5. startup sequence explanation,
6. shutdown sequence explanation,
7. dependency graph explanation,
8. telemetry design explanation,
9. security considerations,
10. guardrails initialization explanation,
11. and any trade-offs made.

---

# Architecture Expectations

The resulting bootstrap layer must support:

- horizontal scaling,
- multiple LLM providers,
- multiple vector databases,
- background workers,
- streaming responses,
- distributed tracing,
- future microservice extraction,
- and zero-downtime deployments

without major refactoring.

---

# Final Instruction

Generate **complete, production-ready code**.

Do not return partial implementations, placeholders, pseudocode, or tutorial-style examples.

If a design decision is ambiguous, choose the option that best preserves:

- Clean Architecture,
- dependency inversion,
- observability,
- security,
- and guardrail enforcement.

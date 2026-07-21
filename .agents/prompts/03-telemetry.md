# Telemetry Module Prompt

## Objective

Implement the **Telemetry Module** for Tailr.

This module provides:

- structured logging,
- distributed tracing,
- metrics collection,
- OpenTelemetry integration,
- Prometheus metrics,
- request/correlation ID propagation,
- workflow-aware context propagation,
- middleware instrumentation,
- exception logging,
- and latency measurement.

The telemetry layer is a **cross-cutting infrastructure concern** and must contain **no business logic**.

---

# Read First

Mandatory documents:

- AGENTS.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/fastapi.md
- rules/security.md
- rules/testing.md
- ADR/02 — Clean Architecture
- ADR/07 — Event-Driven Workflow Engine
- ADR/10 — Evaluation-Driven Development
- ADR/11 — Validation & Guardrails Engine
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs.

---

# Requirements

Implement the following capabilities:

## Structured Logging

- JSON logging by default
- optional human-readable console logging
- consistent field names
- log level configuration
- exception serialization
- context-aware logging
- no `print()` statements

### Required Log Fields

Every log entry must include:

- timestamp
- level
- service
- environment
- request_id
- correlation_id
- trace_id
- span_id
- workflow_id (when available)
- agent_name (when available)
- module
- operation
- duration_ms (when available)
- message

---

# Request ID

Generate a unique request ID for every incoming HTTP request.

### Requirements

- UUIDv7 preferred (UUID4 acceptable if unavailable)
- returned in `X-Request-ID`
- included in all logs
- propagated to background tasks
- propagated to outbound HTTP requests

If the client provides a request ID, validate and reuse it.

---

# Correlation ID

Support distributed request correlation.

### Requirements

- header: `X-Correlation-ID`
- generate if missing
- propagate across async boundaries
- include in logs, traces, and metrics labels (low-cardinality usage only)

---

# Context Propagation

Use `contextvars` for async-safe propagation.

### Required Context

- request_id
- correlation_id
- trace_id
- workflow_id
- agent_name
- user_id (when authenticated)

Context must be accessible from:

- middleware,
- services,
- repositories,
- workflow engine,
- background jobs,
- and guardrails.

---

# OpenTelemetry

Configure OpenTelemetry for:

- FastAPI
- HTTPX
- SQLAlchemy
- Redis
- background tasks
- custom workflow spans

### Required Features

- W3C trace context propagation
- configurable sampling ratio
- OTLP exporter
- console exporter (development)
- resource attributes
- graceful shutdown

### Resource Attributes

- service.name = tailr-backend
- service.version
- deployment.environment

---

# Tracing

Create spans for:

## HTTP Requests

- route
- method
- status code
- duration

## Database Operations

- query type
- table
- duration

## Workflow Execution

- workflow_id
- workflow_name
- current_state
- retry_count

## Agent Execution

- agent_name
- prompt_version
- model_name
- token_count
- latency_ms

## Guardrails

- profile_name
- validator_name
- validation_status
- repair_applied

---

# Prometheus Metrics

Expose `/metrics`.

### Required Metrics

#### HTTP

- http_requests_total
- http_request_duration_seconds
- http_requests_in_progress

#### Database

- db_query_duration_seconds
- db_connections_active

#### AI

- llm_requests_total
- llm_request_duration_seconds
- llm_tokens_total
- llm_provider_failures_total

#### Workflow

- workflow_executions_total
- workflow_duration_seconds
- workflow_failures_total
- workflow_retries_total

#### Guardrails

- guardrail_validations_total
- guardrail_rejections_total
- guardrail_repairs_total
- hallucination_detections_total
- prompt_injection_detections_total

#### Evaluation

- evaluation_runs_total
- evaluation_failures_total

### Label Rules

Allowed labels:

- method
- route
- status
- provider
- model
- workflow
- agent
- validator
- environment

Do **not** use request IDs or user IDs as metric labels.

---

# Middleware

Implement telemetry middleware for:

## Request Context

- request ID
- correlation ID
- trace context

## Structured Access Logging

Log:

- method
- path
- status
- client IP
- user agent
- duration

## Metrics Collection

- request counters
- latency histograms
- in-flight gauge

## Exception Instrumentation

- uncaught exceptions
- stack traces
- trace correlation
- sanitized error messages

Middleware must be async-compatible and non-blocking.

---

# Exception Logging

Implement centralized exception logging.

### Requirements

- structured exception events
- stack trace capture
- trace correlation
- request context
- workflow context
- guardrail context
- and error classification

### Never Log

- passwords
- API keys
- authorization headers
- JWTs
- raw uploaded resumes
- or other sensitive PII

Sensitive fields must be automatically redacted.

---

# Guardrails Telemetry

Emit telemetry for every validation run.

### Required Fields

- workflow_id
- agent_name
- profile_name
- validator_name
- status
- repair_applied
- violation_code
- execution_time_ms

### Metrics

- pass rate
- rejection rate
- repair rate
- validator latency
- hallucination detection count
- prompt injection detection count

These metrics are required for EDD dashboards.

---

# Workflow Telemetry

Instrument the workflow engine.

### Emit Events

- workflow_started
- workflow_checkpoint_created
- workflow_resumed
- workflow_retried
- workflow_completed
- workflow_failed
- workflow_cancelled

### Include

- workflow_id
- state
- retry_count
- duration
- trigger_source

---

# HTTP Client Instrumentation

Instrument outbound HTTP calls.

### Capture

- method
- host
- path template
- status code
- duration
- retry count

### Propagate Headers

- traceparent
- tracestate
- X-Request-ID
- X-Correlation-ID

---

# Logging Configuration

Support:

## Development

- pretty console logs
- colored output
- debug level
- local trace exporter

## Testing

- minimal noise
- deterministic timestamps (where possible)
- capture logs for assertions

## Production

- JSON logs
- INFO level by default
- OTLP exporter
- Prometheus enabled
- sampling enabled

---

# Required File Structure

Generate production-ready files:

```text
telemetry/
├── __init__.py
├── config.py
├── logging.py
├── metrics.py
├── tracing.py
├── context.py
├── middleware.py
├── exceptions.py
├── exporters.py
├── propagation.py
├── workflow.py
├── guardrails.py
├── instrumentation/
│   ├── fastapi.py
│   ├── httpx.py
│   ├── sqlalchemy.py
│   └── redis.py
└── docs/
    ├── logging.md
    ├── metrics.md
    └── tracing.md
```

---

# Configuration

Generate typed configuration examples for:

```env
LOG_LEVEL=INFO
LOG_FORMAT=json

OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SAMPLING_RATIO=0.2

PROMETHEUS_ENABLED=true
PROMETHEUS_PREFIX=tailr

ENABLE_REQUEST_LOGGING=true
ENABLE_SQL_TRACING=true
```

Validate all telemetry configuration at startup.

---

# Testing Requirements

Generate tests for:

- request ID generation
- correlation ID propagation
- context propagation across async tasks
- JSON log formatting
- exception logging
- metrics registration
- metrics endpoint
- trace context propagation
- workflow span creation
- guardrail telemetry emission
- and middleware latency measurement

Use:

- pytest
- pytest-asyncio
- httpx.AsyncClient
- caplog
- OpenTelemetry in-memory exporters
- Prometheus test registry

Tests must be deterministic.

---

# Documentation Requirements

Generate documentation covering:

- logging format
- correlation strategy
- tracing architecture
- metric naming conventions
- dashboard examples
- alerting recommendations
- local observability setup
- and troubleshooting steps

Include example log entries and example Prometheus queries.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- avoid global mutable state,
- be async-safe,
- have minimal performance overhead,
- support graceful shutdown,
- and be production deployable.

### Additional Constraints

- no blocking I/O in middleware,
- no high-cardinality metric labels,
- no duplicate log emission,
- and no hidden background threads.

---

# Output Requirements

Return:

1. complete production-ready source files,
2. middleware implementations,
3. configuration examples,
4. test files,
5. telemetry documentation,
6. example log output,
7. example metrics output,
8. trace propagation explanation,
9. performance considerations,
10. security considerations,
11. and any trade-offs made.

Do not return partial implementations, placeholders, or tutorial-style examples.

---

# Final Instruction

Generate a **complete production-ready telemetry module** that provides:

- structured observability,
- distributed tracing,
- metrics,
- workflow instrumentation,
- guardrails instrumentation,
- evaluation telemetry,
- and secure context propagation

for the entire Tailr platform.

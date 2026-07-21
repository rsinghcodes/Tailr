# Production Hardening — Production Implementation Prompt

## Objective

Implement the complete production-ready **Production Hardening Module** for Tailr.

This module transforms the development environment into a production-grade deployment with containerization, health monitoring, observability, CI/CD, performance optimization, and operational readiness.

The Production Hardening Module is responsible for:

- Docker containerization,
- Docker Compose orchestration,
- health check implementation,
- readiness and liveness probes,
- Prometheus metrics exposure,
- distributed tracing configuration,
- structured logging in production mode,
- CI/CD pipeline (GitHub Actions),
- caching strategy,
- performance optimization,
- security hardening,
- observability dashboards,
- graceful shutdown,
- zero-downtime deployment support,
- and operational documentation.

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
- 14-Deployment.md
- 15-Observability.md
- 16-Security.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Deployment Philosophy

- **Local First** — every component runs locally, no cloud dependency
- **Container Native** — every service runs inside Docker
- **Cloud Ready** — same images deploy to any cloud
- **Reproducible** — deterministic builds and deployments

---

# Docker

## Backend Dockerfile

### Requirements

- multi-stage build (builder + runtime)
- Python 3.13 slim base
- non-root user
- minimal image size
- dependency caching
- health check instruction
- proper signal handling (PID 1)
- no development dependencies in production image

## Frontend Dockerfile

### Requirements

- multi-stage build (builder + runtime)
- Node.js LTS base
- static asset optimization
- Nginx for serving

## Ollama Container

- GPU passthrough support (when available)
- model preloading
- health check

---

# Docker Compose

## Services

```yaml
services:
  backend:      # FastAPI application
  frontend:     # Next.js application
  postgres:     # PostgreSQL 17
  redis:        # Redis 7
  qdrant:       # Qdrant vector database
  ollama:       # LLM inference server
  prometheus:   # Metrics collection
  grafana:      # Dashboards (optional)
  jaeger:       # Distributed tracing (optional)
```

### Requirements

- service dependency ordering
- health check configuration for each service
- volume mounts for data persistence
- network isolation
- environment variable configuration
- GPU support for Ollama (optional)
- development and production profiles

### Profiles

- `default` — core services (backend, postgres, redis, qdrant, ollama)
- `monitoring` — adds prometheus, grafana, jaeger
- `full` — all services

---

# Health Checks

## Application Health

### `/health/live`

Returns application process status. Lightweight, no dependency checks.

### `/health/ready`

Verifies:

- PostgreSQL connectivity
- Redis connectivity
- Qdrant connectivity
- LLM provider availability
- Prompt registry availability
- Guardrails registry availability

A service that is "up" but cannot run Guardrails must not report ready.

### `/health/startup`

Returns whether startup completed successfully. Used by Kubernetes startup probes.

### Response Format

```json
{
  "status": "ready",
  "checks": {
    "postgres": { "status": "ok", "latency_ms": 2 },
    "redis": { "status": "ok", "latency_ms": 1 },
    "qdrant": { "status": "ok", "latency_ms": 5 },
    "llm": { "status": "ok", "latency_ms": 150 },
    "guardrails": { "status": "ok" }
  },
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2026-07-20T10:00:00Z"
}
```

---

# Observability

## Prometheus Metrics

Expose `/metrics` endpoint.

### Required Metrics

- HTTP: requests_total, request_duration_seconds, requests_in_progress
- Database: query_duration_seconds, connections_active
- AI: llm_requests_total, llm_request_duration_seconds, llm_tokens_total, llm_provider_failures_total
- Workflow: workflow_executions_total, workflow_duration_seconds, workflow_failures_total, workflow_retries_total
- Guardrails: guardrail_validations_total, guardrail_rejections_total, guardrail_repairs_total, hallucination_detections_total, prompt_injection_detections_total
- Evaluation: evaluation_runs_total, evaluation_failures_total

## Distributed Tracing

- OpenTelemetry integration
- OTLP exporter to Jaeger
- W3C trace context propagation
- configurable sampling ratio
- trace propagation across workflows and guardrails

## Structured Logging

- JSON format in production
- request_id, correlation_id, trace_id in every log
- log level configuration
- log rotation support
- no sensitive data in logs

---

# CI/CD Pipeline

## GitHub Actions

### Workflow Steps

```yaml
1. Checkout code
2. Set up Python 3.13
3. Install dependencies
4. Ruff (linting)
5. Black (formatting check)
6. MyPy (type checking)
7. Pytest - unit tests
8. Pytest - integration tests (Testcontainers)
9. Pytest - guardrail tests
10. Coverage report (enforce minimums)
11. Build Docker image
12. Push to registry (on main branch)
13. Deploy to staging (on main branch)
```

### Branch Rules

- `main` — deploy to staging
- `release/*` — deploy to production
- `feature/*` — run tests only

### Quality Gates

- Ruff must pass
- MyPy must pass
- Coverage minimums enforced
- No critical vulnerabilities in dependencies

---

# Caching Strategy

## Redis Caching

- embedding results
- retrieval results (when appropriate)
- prompt templates
- parsed resume models (short TTL)
- API rate limiting counters

### Cache Invalidation

- TTL-based expiration
- explicit invalidation on data change
- never cache guardrail results independently of content

## HTTP Caching

- ETag support for resume resources
- Cache-Control headers for static assets

---

# Performance Optimization

## Database

- connection pooling (pool_size from settings)
- N+1 query prevention (selectinload, joinedload)
- query optimization (avoid SELECT *)
- slow query logging (> configurable threshold)
- index optimization

## AI

- batch embeddings
- reuse HTTP clients
- connection pooling for LLM providers
- stream LLM output for progress
- run independent guardrail validators concurrently

## Application

- async-first everywhere
- no synchronous I/O
- resource cleanup on shutdown
- memory-efficient streaming

---

# Security Hardening

## Production Checklist

- HTTPS enforced
- HSTS enabled
- security headers configured
- CORS restricted to allowed origins
- rate limiting active
- file upload limits enforced
- debug mode disabled
- stack traces not exposed
- secrets from environment only
- non-root container user
- dependency vulnerability scanning
- guardrails registry verified at startup

---

# Graceful Shutdown

### Requirements

- drain active requests
- complete in-flight workflows (or checkpoint)
- close database connections
- close Redis connections
- close HTTP clients
- flush telemetry exporters
- timeout-aware shutdown (configurable)
- idempotent cleanup
- structured shutdown logging

---

# Required File Structure

```text
deployment/
├── docker/
│   ├── backend/
│   │   └── Dockerfile
│   ├── frontend/
│   │   └── Dockerfile
│   └── ollama/
│       └── Dockerfile
├── docker-compose.yml
├── docker-compose.monitoring.yml
├── .env.example
├── .env.production.example
├── nginx/
│   └── nginx.conf
└── scripts/
    ├── setup.sh
    ├── healthcheck.sh
    └── backup.sh

.github/
└── workflows/
    ├── ci.yml
    ├── deploy-staging.yml
    └── deploy-production.yml
```

---

# Testing Requirements

Generate tests for:

- Docker build success,
- Docker Compose startup (all services),
- health endpoint responses,
- readiness checks (all dependencies),
- Prometheus metrics exposure,
- graceful shutdown behavior,
- CI pipeline configuration validation,
- cache operations (hit, miss, invalidation),
- performance benchmarks (response latency, throughput),
- and security hardening verification.

---

# Quality Requirements

Generated configuration must:

- be production-ready,
- be reproducible,
- support local development,
- support CI/CD,
- contain no hardcoded secrets,
- and include comprehensive documentation.

---

# Output Requirements

Return:

1. complete Dockerfiles,
2. Docker Compose configuration,
3. GitHub Actions workflows,
4. Nginx configuration,
5. environment variable examples,
6. health check implementation,
7. monitoring setup guide,
8. deployment documentation,
9. performance tuning guide,
10. security hardening checklist,
11. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Production Hardening Module** that provides:

- containerized deployment,
- health monitoring,
- observability (metrics, tracing, logging),
- CI/CD automation,
- caching,
- performance optimization,
- security hardening,
- graceful shutdown,
- and comprehensive operational documentation

for the entire Tailr platform.

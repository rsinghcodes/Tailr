# Configuration Module Prompt

## Objective

Build the **typed configuration system** for Tailr.

The configuration layer is responsible for:

- environment variable loading,
- validation,
- secrets management,
- environment separation,
- provider configuration,
- telemetry configuration,
- guardrails configuration,
- and startup-time configuration verification.

This module is part of the **bootstrap/infrastructure layer** and must contain **no business logic**.

---

# Read First

Mandatory documents:

- AGENTS.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/security.md
- rules/testing.md
- ADR-0002 — Clean Architecture
- ADR-0008 — LLM Router & Provider Abstraction Layer
- ADR-0011 — Validation & Guardrails Engine
- 20-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs.

---

# Requirements

Implement a **Pydantic v2 BaseSettings** based configuration system with:

- environment variable loading,
- typed settings,
- nested configuration objects,
- validation,
- secrets handling,
- environment separation,
- startup verification,
- and `.env` support.

---

# Supported Environments

Support the following environments:

- development
- testing
- staging
- production

Environment selection must be controlled by:

```bash
APP_ENV=development
```

The environment value must be validated against an enum.

---

# Required Configuration Domains

Implement typed settings for:

## Application

- app_name
- app_version
- environment
- debug
- api_prefix
- allowed_hosts

---

## PostgreSQL

- host
- port
- database
- username
- password
- pool_size
- max_overflow
- echo_sql (development only)

Generate both:

- async SQLAlchemy URL
- sync migration URL

---

## Redis

- host
- port
- password
- database
- SSL enabled
- connection timeout

---

## Qdrant

- host
- port
- api_key
- collection_name
- prefer_grpc
- timeout_seconds

---

## LLM Router

Implement provider-aware configuration.

### Ollama

- base_url
- default_model
- timeout_seconds

### OpenAI (future-ready)

- api_key
- base_url
- default_model

### Anthropic (future-ready)

- api_key
- default_model

### Routing

- default_provider
- fallback_provider
- enable_fallback
- request_timeout_seconds

---

## Embeddings

- model_name
- dimension
- batch_size
- device
- normalize_embeddings

---

## Guardrails

- enabled
- default_profile
- strict_mode
- enable_hallucination_detection
- enable_prompt_injection_detection
- enable_pii_scanning
- enable_latex_validation
- repair_enabled

### Profile Thresholds

- rewrite_strict
- analysis_standard
- validation_paranoid

---

## Telemetry

### Logging

- log_level
- log_format (json/text)
- enable_request_logging

### OpenTelemetry

- enabled
- service_name
- exporter_endpoint
- sampling_ratio

### Metrics

- enable_prometheus
- metrics_prefix

---

## Security

- jwt_secret_key
- jwt_algorithm
- access_token_expire_minutes
- enable_https_redirect
- enable_hsts
- cors_allowed_origins
- max_upload_size_mb

---

## Workflow Engine

- max_concurrent_workflows
- workflow_timeout_seconds
- retry_attempts
- retry_backoff_seconds
- checkpoint_enabled

---

# Validation Rules

Implement strict validation.

## Examples

### Port Validation

- 1–65535

### Sampling Ratio

- 0.0–1.0

### Upload Size

- positive integer

### CORS Origins

- valid URLs or explicit localhost values

### Environment

- must match supported enum values

Invalid configuration must raise a clear `ValidationError`.

---

# Secrets Handling

Use:

- `SecretStr`
- `SecretBytes`

Requirements:

- never print secrets,
- never include secrets in `repr`,
- never include secrets in logs,
- and support secret rotation through environment variables.

---

# Environment File Support

Support layered `.env` loading.

Order:

```text
.env
.env.local
.env.<environment>
.env.<environment>.local
```

Environment-specific files should override base values.

---

# Startup Verification

Implement a `validate_runtime_configuration()` function that verifies:

- required secrets are present,
- production does not run with debug enabled,
- HTTPS settings are correct,
- fallback providers are valid,
- guardrail profiles exist,
- telemetry configuration is complete,
- and upload limits are within safe bounds.

This function should be called during application startup.

---

# Required File Structure

Generate production-ready files:

```text
config/
├── __init__.py
├── settings.py
├── enums.py
├── validators.py
├── secrets.py
├── runtime.py
├── factories.py
└── profiles/
    ├── development.py
    ├── testing.py
    ├── staging.py
    └── production.py
```

---

# Example Environment Variables

Generate a complete `.env.example` containing all supported variables.

Example categories:

```env
APP_ENV=development

POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost

QDRANT_HOST=localhost

OLLAMA_BASE_URL=http://localhost:11434

GUARDRAILS_ENABLED=true

OTEL_ENABLED=false
```

Include comments for every variable.

---

# Testing Requirements

Generate tests for:

- environment loading,
- nested settings parsing,
- enum validation,
- invalid port values,
- missing required secrets,
- production safety checks,
- DSN generation,
- guardrail profile validation,
- telemetry validation,
- and `.env` precedence.

Use:

- pytest
- monkeypatch
- temporary environment variables
- temporary `.env` files

Tests must be deterministic.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- avoid global mutable state,
- avoid import-time side effects,
- and be production deployable.

Use:

- `SettingsConfigDict`
- computed properties
- cached settings factory (`@lru_cache`)
- and explicit validation methods.

---

# Output Requirements

Return:

1. complete source files,
2. `.env.example`,
3. test files,
4. explanation of configuration hierarchy,
5. explanation of environment precedence,
6. secret-handling explanation,
7. startup validation explanation,
8. guardrails configuration explanation,
9. telemetry configuration explanation,
10. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready configuration module** that supports:

- local development,
- automated testing,
- staging deployments,
- production deployments,
- multiple LLM providers,
- guardrails enforcement,
- telemetry,
- and future microservice extraction

without requiring architectural changes.

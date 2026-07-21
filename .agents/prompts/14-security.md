# Security — Production Implementation Prompt

## Objective

Implement the complete production-ready **Security Module** for Tailr.

This module enforces security across every layer — from file uploads to AI output rendering — ensuring that user data, AI workflows, infrastructure, and generated artifacts are protected from unauthorized access, malicious inputs, prompt injection, hallucinated content, data leakage, and system abuse.

The Security Module is responsible for:

- JWT authentication,
- resource-level authorization (RBAC),
- rate limiting,
- file upload validation,
- prompt injection protection,
- input sanitization,
- output escaping,
- secrets management,
- HTTP security headers,
- CORS configuration,
- LaTeX sandbox security,
- PII protection,
- audit logging,
- and dependency vulnerability management.

Because Tailr is an **AI-native application**, its security model extends beyond traditional web security to include LLM security, RAG security, vector database protection, and AI workflow isolation.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/security.md
- rules/fastapi.md
- rules/testing.md
- rules/logging.md
- ADR-0002 — Clean Architecture
- ADR-0011 — Validation & Guardrails Engine
- 16-Security.md
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Security Principles

- **Zero Trust** — every request is untrusted, every component validates inputs
- **Least Privilege** — every service receives only required permissions
- **Defense in Depth** — security at every layer (Infrastructure → API → Application → AI → Guardrails → Database → Storage)
- **Secure by Default** — unsafe configuration is never the default
- **Privacy First** — user data never shared without explicit consent
- **Audit Everything** — security events logged for investigation

---

# Authentication

## JWT Bearer Token

### Requirements

- token extraction from `Authorization: Bearer <token>` header
- HS256/RS256 signature validation
- expiration validation
- issuer and audience validation
- typed `get_current_user()` dependency
- refresh token support
- token revocation capability

### Configuration

- `JWT_SECRET_KEY` — from environment, never hardcoded
- `JWT_ALGORITHM` — configurable (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` — configurable
- `REFRESH_TOKEN_EXPIRE_DAYS` — configurable

### Future

- OAuth 2.0 / OpenID Connect
- GitHub Login
- Google Login

---

# Authorization

## Resource-Level Access Control

### Requirements

- verify resource ownership on every request
- deny-by-default authorization
- never trust frontend permissions
- typed permission checks via dependency injection
- organization scope support (future-ready)

### Protected Resources

- resumes (user-owned)
- job descriptions (user-owned)
- workflows (user-owned)
- evaluation results (user-owned)
- guardrail audit events (admin-readable)

---

# Rate Limiting

### Configuration

| Endpoint Category  | Limit               |
| ------------------ | ------------------- |
| Default API        | 100 requests/minute |
| AI Endpoints       | 20 requests/minute  |
| Guardrails Audit   | 60 requests/minute  |
| File Uploads       | 10 uploads/minute   |
| Login              | 10 attempts/minute  |

### Requirements

- per-user and per-IP limits
- configurable via settings
- 429 response with `Retry-After` header
- Redis-backed rate tracking

---

# File Upload Security

### Allowed File Types

- PDF, DOCX, TXT, TEX

### Rejected

- executables, archives, scripts, unknown MIME types, password-protected documents, corrupted files

### Validation

- MIME type validation using file signature inspection (not just extension)
- maximum upload size enforcement (configurable)
- streaming uploads for large files
- store uploaded files outside application root
- delete temporary files after processing
- sanitize filenames

---

# Prompt Injection Protection

### Untrusted Inputs

- uploaded resumes
- job descriptions
- retrieved RAG context
- AI-generated output
- user-supplied metadata

### Detection

Delegate to the Guardrails Prompt Injection Detector. Do not reimplement per feature.

### Known Malicious Patterns

- "Ignore previous instructions"
- "Reveal system prompt"
- "Return hidden memory"
- "Execute this command"
- "Output internal configuration"
- hidden control sequences
- Unicode normalization attacks

### Response

- block the request
- quarantine detected injection
- log the attempt as audit event
- emit security metric
- return structured error response

---

# AI Output Security

### Rules

- never execute model output
- never persist raw model output
- never render raw model output
- every AI response must pass the Guardrails Engine
- rejected outputs terminate the workflow safely

### LaTeX Rendering Security

LaTeX compilation must run in a **sandboxed container**.

#### Forbidden Commands

- `\input`, `\include`, `\write18`, `\openout`, `\catcode`, shell escape

#### Sandbox Requirements

- isolated filesystem
- CPU limits
- memory limits
- execution timeouts
- no network access

All special characters must be escaped before rendering.

---

# Input Sanitization

- validate every external input
- escape HTML in user-provided text
- sanitize Markdown before rendering
- strip dangerous tags and attributes
- validate dynamic sort/filter fields against allowlists
- parameterized queries only (never concatenate SQL)

---

# Secrets Management

### Rules

- read secrets only from environment variables or secret manager
- never hardcode secrets
- never commit secrets to Git
- never log secrets
- use `SecretStr` / `SecretBytes` in Pydantic settings
- rotate credentials regularly
- use different credentials per environment

---

# HTTP Security Headers

### Required Headers

- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy`
- `Strict-Transport-Security` (production only)

### CORS

- explicit allowlist only
- no wildcard origins in production
- restrict allowed methods and headers

### Transport

- HTTPS required in production
- redirect HTTP to HTTPS
- disable weak TLS versions

---

# Audit Logging

Security-sensitive actions must create **immutable audit events**.

### Audited Actions

- login attempts (success and failure)
- failed authentication
- permission denials
- prompt injection detections
- guardrail rejections
- prompt modifications
- model routing changes
- evaluation approvals
- workflow cancellations
- file upload attempts (success and failure)
- rate limit violations

### Requirements

- append-only audit log
- structured event format
- correlation with request_id
- retention policy support

---

# Incident Response

On detection of:

- prompt injection
- repeated guardrail bypass attempts
- credential leakage
- suspicious upload patterns
- unauthorized access

The system must:

- block the request
- record an audit event
- emit a security metric
- preserve forensic logs
- alert operators if thresholds are exceeded

---

# Required File Structure

```text
security/
├── __init__.py
├── authentication/
│   ├── __init__.py
│   ├── jwt.py
│   ├── dependencies.py
│   └── models.py
├── authorization/
│   ├── __init__.py
│   ├── policies.py
│   └── dependencies.py
├── rate_limiting/
│   ├── __init__.py
│   ├── limiter.py
│   └── middleware.py
├── file_validation/
│   ├── __init__.py
│   ├── validator.py
│   └── mime.py
├── sanitization/
│   ├── __init__.py
│   ├── input.py
│   └── output.py
├── headers/
│   ├── __init__.py
│   └── middleware.py
├── audit/
│   ├── __init__.py
│   ├── logger.py
│   └── models.py
└── exceptions.py
```

---

# Testing Requirements

Generate tests for:

- JWT validation (valid, expired, malformed, missing),
- authorization (owner access, non-owner access, admin access),
- rate limiting (within limit, exceeded, reset),
- file upload validation (valid types, rejected types, oversized, corrupted),
- prompt injection detection (known patterns, clean input),
- input sanitization (XSS payloads, SQL injection patterns),
- LaTeX safety (forbidden commands, safe commands),
- security headers (presence, correct values),
- CORS configuration,
- secrets handling (no leakage in logs, no leakage in repr),
- audit event emission,
- and incident response behavior.

Use: pytest, pytest-asyncio, httpx.AsyncClient.

Target coverage: **95%+** for security modules.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- be async-first,
- avoid global mutable state,
- and be production deployable.

---

# Output Requirements

Return:

1. complete source files,
2. test files,
3. security architecture diagram,
4. authentication flow explanation,
5. authorization model explanation,
6. file validation explanation,
7. prompt injection protection explanation,
8. LaTeX sandbox configuration,
9. audit logging schema,
10. security review checklist,
11. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Security Module** that provides:

- JWT authentication,
- resource-level authorization,
- rate limiting,
- file upload security,
- prompt injection protection,
- LaTeX sandbox security,
- input sanitization,
- security headers,
- audit logging,
- incident response,
- and comprehensive security testing

for the entire Tailr platform.

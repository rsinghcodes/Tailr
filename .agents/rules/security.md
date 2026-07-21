---
trigger: always_on
---

# Security Rules

Priority: CRITICAL

---

# Core Principle

Validate everything.

Trust nothing.

Assume all external input is potentially malicious, including:

- uploaded resumes,
- job descriptions,
- retrieved RAG context,
- AI-generated output,
- external API responses,
- and user-supplied metadata.

Security is enforced through deterministic validation and mandatory guardrails.

---

# Upload Security

## Allowed File Types

- PDF
- DOCX
- TXT

## Rejected File Types

- Executables
- Archives (ZIP, RAR, 7z)
- Scripts
- Unknown MIME types
- Password-protected documents
- Corrupted files

MIME type must be validated using file signature inspection, not only the file extension.

---

# Upload Limits

- Maximum upload size is configurable.
- Oversized files must be rejected before processing.
- Streaming uploads should be preferred for large files.
- Uploaded files must be stored outside the application root.
- Temporary files must be deleted after processing.

---

# Authentication

Current:

- JWT access tokens

Future:

- OAuth 2.0 / OpenID Connect

Not allowed:

- server-side sessions,
- unsigned tokens,
- custom authentication schemes.

Tokens must have:

- expiration,
- issuer,
- audience,
- and signature validation.

---

# Authorization

Always verify resource ownership.

Never trust frontend permissions.

Every request accessing a resume, workflow, prompt, or evaluation must validate:

- authenticated user,
- resource ownership,
- organization scope (future),
- and action permissions.

Use deny-by-default authorization.

---

# Secrets Management

- Read secrets only from environment variables or a secret manager.
- Never hardcode secrets.
- Never commit secrets to Git.
- Never log secrets.
- Rotate credentials regularly.
- Use different credentials per environment.

Examples of sensitive values:

- API keys
- database passwords
- JWT signing keys
- OAuth secrets
- cloud credentials
- webhook signing secrets

---

# Prompt Injection Protection

Treat all uploaded resumes as untrusted.

Treat all job descriptions as untrusted.

Treat all retrieved RAG context as untrusted.

Before prompt assembly:

- run prompt injection detection,
- remove malicious instructions,
- strip hidden control sequences,
- normalize Unicode,
- and log detected attacks.

Examples of malicious patterns:

- "Ignore previous instructions"
- "Reveal system prompt"
- "Return hidden memory"
- "Execute this command"
- "Output internal configuration"

Detected injections must be quarantined and excluded from the final prompt.

---

# AI Output Security

Never execute model output.

Never persist raw model output.

Never render raw model output.

Every AI response must pass the Guardrails Engine, including:

- schema validation,
- JSON validation,
- hallucination detection,
- resume integrity validation,
- ATS validation,
- and LaTeX safety validation.

Rejected outputs must terminate the workflow safely.

---

# Hallucination Prevention

The system must reject outputs that introduce:

- employers not present in the Canonical Resume Model,
- projects not present in the source resume,
- technologies not present in the source resume,
- fabricated metrics,
- altered employment dates,
- unsupported certifications.

If supporting evidence is missing, the output must be rejected.

---

# SQL Injection Protection

- Always use parameterized queries.
- Never concatenate SQL strings.
- Use SQLAlchemy query builders or prepared statements.
- Validate dynamic sort and filter fields against allowlists.

---

# Cross-Site Scripting (XSS)

- Escape all rendered HTML.
- Sanitize Markdown before rendering.
- Strip dangerous tags and attributes.
- Use a strict Content Security Policy (CSP).
- Never trust user-generated rich text.

---

# LaTeX Rendering Security

LaTeX compilation must run in a sandboxed container.

Forbidden commands:

- \\input
- \\include
- \\write18
- \\openout
- \\catcode
- shell escape features

All special characters must be escaped before rendering.

Compilation must use:

- isolated filesystem,
- CPU limits,
- memory limits,
- execution timeouts,
- and no network access.

---

# Dependency Security

- Keep packages updated.
- Review CVEs regularly.
- Pin dependency versions.
- Use automated vulnerability scanning.
- Remove unused dependencies.
- Verify licenses for new packages.

CI must fail on critical vulnerabilities.

---

# HTTP Security

## Required Headers

- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy
- Strict-Transport-Security (production)

## Transport

- HTTPS required in production.
- Redirect HTTP to HTTPS.
- Disable weak TLS versions.

## CORS

- Explicit allowlist only.
- No wildcard origins in production.
- Restrict allowed methods and headers.

---

# Rate Limiting

Apply rate limits to:

- login endpoints,
- file uploads,
- workflow creation,
- LLM generation endpoints,
- evaluation endpoints.

Use configurable per-user and per-IP limits.

---

# Logging Security

Never log:

- passwords,
- tokens,
- API keys,
- authorization headers,
- personal identification numbers,
- or raw uploaded documents.

Structured logs must include:

- request_id,
- correlation_id,
- user_id (when available),
- client IP,
- operation,
- status,
- and duration.

Sensitive fields must be redacted automatically.

---

# Audit Logging

Security-sensitive actions must create immutable audit events.

Examples:

- login attempts,
- failed authentication,
- permission denials,
- prompt injection detections,
- guardrail rejections,
- prompt modifications,
- model routing changes,
- evaluation approvals,
- and workflow cancellations.

Audit logs must be append-only and retained according to policy.

---

# Data Protection

- Encrypt data in transit.
- Encrypt sensitive data at rest where applicable.
- Minimize stored personal data.
- Support future data deletion/export requirements.
- Avoid storing unnecessary resume artifacts.

---

# Operational Security

- Run services with least privilege.
- Use non-root containers.
- Isolate worker processes.
- Restrict outbound network access where possible.
- Enable distributed tracing for incident investigation.
- Monitor abnormal token usage and workflow activity.

---

# Incident Response

On detection of:

- prompt injection,
- repeated guardrail bypass attempts,
- credential leakage,
- suspicious upload patterns,
- or unauthorized access,

the system must:

- block the request,
- record an audit event,
- emit a security metric,
- preserve forensic logs,
- and alert operators if thresholds are exceeded.

---

# Security Review Checklist

Before merging any feature, verify:

- [ ] Input validation implemented
- [ ] Authorization checks added
- [ ] Guardrails enforced
- [ ] Prompt injection protection added
- [ ] Secrets handled securely
- [ ] Structured logging added
- [ ] Audit events generated
- [ ] Dependencies reviewed
- [ ] LaTeX rendering remains sandboxed
- [ ] No raw AI output is persisted or rendered

If any item is unchecked, the change is not production-ready.

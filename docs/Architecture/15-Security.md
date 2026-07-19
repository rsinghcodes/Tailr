# Security Architecture

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the security architecture of Tailr.

Security protects user data, AI workflows, infrastructure, generated artifacts, and AI-generated outputs from unauthorized access, malicious inputs, prompt injection, hallucinated content, data leakage, and system abuse.

Because Tailr is an AI-native application, its security model extends beyond traditional web security to include LLM security, RAG security, vector database protection, and AI workflow isolation.

---

# 2. Security Goals

The platform must:

- Protect user resumes
- Prevent unauthorized access
- Secure AI interactions
- Prevent prompt injection
- Detect hallucinated content
- Protect vector data
- Ensure secure file processing
- Prevent data leakage
- Enforce guardrail policies
- Support auditability

---

# 3. Security Principles

Tailr follows six core principles.

## Zero Trust

Every request is untrusted.

Every component validates its inputs.

---

## Least Privilege

Every service receives only the permissions it requires.

---

## Defense in Depth

Security exists at multiple layers.

Infrastructure
↓
API
↓
Application
↓
AI
↓
Guardrails
↓
Database
↓
Storage

---

## Secure by Default

Unsafe configuration is never the default.

---

## Privacy First

User data is never shared with external services unless explicitly configured.

---

## Audit Everything

Security events are logged for investigation.

---

# 4. Threat Model

Major threats include

- Unauthorized access
- Resume theft
- Prompt injection
- Prompt leakage
- Hallucinated resume content
- Malicious LaTeX
- API abuse
- Vector poisoning
- Model jailbreak
- File upload attacks
- Data leakage
- Denial of Service

Each threat has dedicated mitigation.

---

# 5. Authentication

Version 1

JWT Authentication

```
Authorization

Bearer <token>
```

Future

- OAuth2
- Google Login
- GitHub Login
- Multi-factor Authentication

---

# 6. Authorization

Role-Based Access Control (RBAC)

Roles

```
User

Admin

System
```

Every request verifies ownership before accessing resources.

---

# 7. Password Security

Passwords

- Argon2 hashing
- Strong password policy
- Password reset tokens
- Expiring reset links

Passwords are never stored in plaintext.

---

# 8. API Security

Every endpoint enforces

- Authentication
- Authorization
- Rate limiting
- Input validation
- Output sanitization

Sensitive endpoints require valid JWTs.

---

# 9. Input Validation

Validate

- File size
- MIME type
- UTF-8 encoding
- JSON schema
- String length
- Allowed characters
- Prompt injection patterns
- Embedded control instructions

Reject malformed or suspicious input immediately.

---

# 10. File Upload Security

Supported files

- .tex

Future

- PDF
- DOCX

Checks

- File extension
- MIME verification
- Size limits
- Malware scan (future)
- Template validation

Executable files are rejected.

---

# 11. LaTeX Security

Generated LaTeX is sandboxed.

Blocked commands include

```
\write18

\input

\include

\openout

\read

\catcode
```

Only a safe subset of LaTeX commands is allowed.

---

# 12. LLM Security

System prompts are immutable.

User content is always treated as untrusted.

The model never receives unrestricted system access.

Prompt construction separates

- system instructions
- retrieved context
- user content

Every model response passes through the Guardrails layer before it is accepted by the application.

---

# 13. Prompt Injection Protection

Potential attacks

```
Ignore previous instructions

Reveal system prompt

Delete validation

Return hidden data
```

Mitigation

- Context isolation
- Prompt delimiters
- Structured output enforcement
- Output validation
- Retrieval filtering
- Prompt injection detection
- Automatic request rejection for high-risk patterns

Prompt injection attempts are logged and included in security telemetry.

---

# 14. Guardrails Security

The Guardrails layer enforces AI safety policies independently of the underlying model provider.

Guardrails perform

- JSON schema validation
- Prompt injection detection
- Prompt leakage detection
- Hallucination detection
- Resume integrity validation
- ATS formatting validation
- PII detection
- Toxicity detection
- Output repair when possible

Outputs that fail critical guardrail checks are rejected and never returned to the user.

## All guardrail decisions are recorded in immutable audit logs.

# 15. RAG Security

Knowledge retrieval only accesses

- User-owned resume
- User-owned workflow
- Public reference knowledge

Cross-user retrieval is prohibited.

Every chunk includes ownership metadata.

Retrieved chunks are also scanned for prompt injection markers before being inserted into the model context.

---

# 16. Vector Database Security

Each vector stores

```
user_id

resume_id

entity_type

visibility
```

Queries are filtered by ownership before retrieval.

Embedding similarity alone never grants access.

Suspicious or poisoned embeddings can be quarantined without affecting other user collections.

---

# 17. Data Privacy

Sensitive data

- Email
- Phone
- Address
- Resume
- Employment history

Never appears in

- Logs
- Metrics
- Exceptions
- Monitoring dashboards
- Raw LLM prompts
- Raw model completions
- Guardrail internal state

PII is masked whenever possible.

---

# 18. Encryption

Data in transit

HTTPS (TLS 1.3)

Data at rest

- PostgreSQL encryption
- Disk encryption
- Object storage encryption

Secrets remain encrypted.

---

# 19. Secrets Management

Secrets include

- JWT secret
- Database credentials
- API keys
- Langfuse keys

Development

```
.env
```

Production

Docker Secrets

Future

Vault

Secrets are never committed to Git.

---

# 20. Database Security

Mitigations

- Parameterized queries
- Least-privilege users
- Encrypted backups
- Connection pooling
- Audit logging

SQL Injection is prevented through ORM usage.

---

# 21. Redis Security

Redis

- Internal network only
- Authentication enabled
- No public exposure

Redis stores only temporary data.

---

# 22. Object Storage Security

Resume files

- Signed URLs
- Access control
- Versioning
- Server-side encryption

Deleted files are securely removed.

---

# 23. Dependency Security

Dependencies are monitored using

- Dependabot
- Safety (Python)
- npm audit
- Trivy (containers)

Outdated packages are reviewed regularly.

---

# 24. Container Security

Containers

- Run as non-root
- Read-only filesystem where possible
- Minimal base images
- Resource limits
- No unnecessary ports

Images are scanned before deployment.

---

# 25. Network Security

Internal services communicate over private Docker networks.

Public exposure is limited to

- Frontend
- API Gateway

Databases remain private.

---

# 26. Logging Security

Logs include

- Request IDs
- Workflow IDs
- Errors

Logs exclude

- Resume text
- JWTs
- Passwords
- API keys
- PII
- Raw prompts
- Raw LLM responses
- Guardrail internal metadata

Sensitive values are automatically redacted.

---

# 27. Rate Limiting

Example limits

API

100 requests/minute

AI Endpoints

20 requests/minute

Authentication

10 attempts/minute

Limits reduce abuse.

---

# 28. Audit Logging

Security events

- Login
- Logout
- Resume upload
- Workflow execution
- Permission failure
- Prompt injection attempt
- Guardrail rejection
- Hallucination detection
- PII detection
- Output repair event

Audit records are immutable.

---

# 29. Incident Response

Detection

↓

Alert

↓

Containment

↓

Investigation

↓

Recovery

↓

Postmortem

Every security incident follows a documented process.

---

# 30. Compliance Considerations

Tailr is designed with principles aligned to

- GDPR
- OWASP ASVS
- OWASP Top 10
- AI security best practices

Formal certification is outside Version 1 scope.

---

# 31. Future Enhancements

Future capabilities

- Multi-factor Authentication
- WebAuthn
- Hardware security keys
- AI content moderation
- Automatic PII detection
- Differential privacy
- Secret rotation
- Policy-based access control (PBAC)
- Adaptive guardrail policies
- Automated hallucination review
- Prompt risk scoring
- Real-time output quarantine
- AI safety policy engine

---

# 32. Security Testing

Security testing includes

- Unit tests
- Integration tests
- Static analysis
- Dependency scanning
- Container scanning
- Prompt injection tests
- Hallucination detection tests
- Guardrail policy tests
- PII leakage tests
- Output repair tests
- Penetration testing
- Fuzz testing

Security tests run automatically in CI/CD.

---

# 33. Architecture Decisions

| Decision                     | Rationale                                  |
| ---------------------------- | ------------------------------------------ |
| JWT Authentication           | Stateless authentication                   |
| RBAC                         | Fine-grained authorization                 |
| HTTPS Everywhere             | Secure communication                       |
| Prompt isolation             | Prevent LLM manipulation                   |
| Guardrails layer             | Provider-independent AI safety enforcement |
| Structured output validation | Prevent malformed AI responses             |
| Ownership-based retrieval    | Prevent cross-user data leakage            |
| Sandboxed LaTeX              | Prevent arbitrary code execution           |
| Structured audit logs        | Traceability and compliance                |

---

# 34. Summary

Tailr adopts a defense-in-depth security architecture that protects both traditional application components and AI-specific workflows.

By combining strong authentication, role-based authorization, secure file processing, prompt injection defenses, hallucination detection, a provider-independent Guardrails layer, retrieval isolation, encrypted storage, and comprehensive audit logging, the platform safeguards sensitive career data while enabling reliable AI-powered resume optimization.

The Guardrails layer ensures that every AI-generated response is validated for safety, structure, and factual integrity before reaching the user, significantly reducing the risk of prompt leakage, malformed outputs, fabricated resume content, and other AI-specific threats.

The security architecture is designed to evolve alongside the platform, supporting future enterprise deployments and advanced AI governance requirements without requiring fundamental redesign.

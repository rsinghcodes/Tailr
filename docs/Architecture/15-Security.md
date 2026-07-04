# Security Architecture

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the security architecture of Tailr.

Security protects user data, AI workflows, infrastructure, and generated artifacts from unauthorized access, malicious inputs, prompt injection, data leakage, and system abuse.

Because Tailr is an AI-native application, its security model extends beyond traditional web security to include LLM security, RAG security, vector database protection, and AI workflow isolation.

---

# 2. Security Goals

The platform must:

- Protect user resumes
- Prevent unauthorized access
- Secure AI interactions
- Prevent prompt injection
- Protect vector data
- Ensure secure file processing
- Prevent data leakage
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

Reject malformed input immediately.

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
- Output validation
- Retrieval filtering

Prompt injection attempts are logged.

---

# 14. RAG Security

Knowledge retrieval only accesses

- User-owned resume
- User-owned workflow
- Public reference knowledge

Cross-user retrieval is prohibited.

Every chunk includes ownership metadata.

---

# 15. Vector Database Security

Each vector stores

```
user_id

resume_id

entity_type

visibility
```

Queries are filtered by ownership before retrieval.

Embedding similarity alone never grants access.

---

# 16. Data Privacy

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

PII is masked whenever possible.

---

# 17. Encryption

Data in transit

HTTPS (TLS 1.3)

Data at rest

- PostgreSQL encryption
- Disk encryption
- Object storage encryption

Secrets remain encrypted.

---

# 18. Secrets Management

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

# 19. Database Security

Mitigations

- Parameterized queries
- Least-privilege users
- Encrypted backups
- Connection pooling
- Audit logging

SQL Injection is prevented through ORM usage.

---

# 20. Redis Security

Redis

- Internal network only
- Authentication enabled
- No public exposure

Redis stores only temporary data.

---

# 21. Object Storage Security

Resume files

- Signed URLs
- Access control
- Versioning
- Server-side encryption

Deleted files are securely removed.

---

# 22. Dependency Security

Dependencies are monitored using

- Dependabot
- Safety (Python)
- npm audit
- Trivy (containers)

Outdated packages are reviewed regularly.

---

# 23. Container Security

Containers

- Run as non-root
- Read-only filesystem where possible
- Minimal base images
- Resource limits
- No unnecessary ports

Images are scanned before deployment.

---

# 24. Network Security

Internal services communicate over private Docker networks.

Public exposure is limited to

- Frontend
- API Gateway

Databases remain private.

---

# 25. Logging Security

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

Sensitive values are automatically redacted.

---

# 26. Rate Limiting

Example limits

API

100 requests/minute

AI Endpoints

20 requests/minute

Authentication

10 attempts/minute

Limits reduce abuse.

---

# 27. Audit Logging

Security events

- Login
- Logout
- Resume upload
- Workflow execution
- Permission failure
- Prompt injection attempt

Audit records are immutable.

---

# 28. Incident Response

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

# 29. Compliance Considerations

Tailr is designed with principles aligned to

- GDPR
- OWASP ASVS
- OWASP Top 10
- AI security best practices

Formal certification is outside Version 1 scope.

---

# 30. Future Enhancements

Future capabilities

- Multi-factor Authentication
- WebAuthn
- Hardware security keys
- AI content moderation
- Automatic PII detection
- Differential privacy
- Secret rotation
- Policy-based access control (PBAC)

---

# 31. Security Testing

Security testing includes

- Unit tests
- Integration tests
- Static analysis
- Dependency scanning
- Container scanning
- Prompt injection tests
- Penetration testing
- Fuzz testing

Security tests run automatically in CI/CD.

---

# 32. Architecture Decisions

| Decision                  | Rationale                        |
| ------------------------- | -------------------------------- |
| JWT Authentication        | Stateless authentication         |
| RBAC                      | Fine-grained authorization       |
| HTTPS Everywhere          | Secure communication             |
| Prompt isolation          | Prevent LLM manipulation         |
| Ownership-based retrieval | Prevent cross-user data leakage  |
| Sandboxed LaTeX           | Prevent arbitrary code execution |
| Structured audit logs     | Traceability and compliance      |

---

# 33. Summary

Tailr adopts a defense-in-depth security architecture that protects both traditional application components and AI-specific workflows.

By combining strong authentication, role-based authorization, secure file processing, prompt injection defenses, retrieval isolation, encrypted storage, and comprehensive audit logging, the platform safeguards sensitive career data while enabling reliable AI-powered resume optimization.

The security architecture is designed to evolve alongside the platform, supporting future enterprise deployments without requiring fundamental redesign.

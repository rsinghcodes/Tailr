# Refactoring — Production Implementation Prompt

## Objective

Perform a comprehensive **architectural refactoring review** of the Tailr codebase.

This prompt guides the identification and resolution of:

- duplicated code,
- architecture violations,
- dead code,
- performance issues,
- security risks,
- oversized functions and classes,
- coupling problems,
- cohesion issues,
- guardrails coverage gaps,
- dependency direction violations,
- and technical debt.

Refactoring must preserve existing behavior while improving architecture, readability, and maintainability.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/fastapi.md
- rules/database.md
- rules/security.md
- rules/testing.md
- rules/logging.md
- rules/ai-agents.md
- rules/rag.md
- rules/prompts.md
- All relevant ADRs
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, the architecture documents take precedence.

---

# Refactoring Principles

- refactor only when complexity decreases, readability improves, architecture improves, performance improves, or test coverage remains
- never refactor for personal preference
- always preserve existing behavior
- every refactoring step must maintain or improve test coverage
- refactoring a guardrail validator requires re-running its adversarial test suite and confirming detection rates have not regressed

---

# Identification Phase

## Code Quality Scan

### Duplicated Code

- identify repeated logic across modules
- identify copy-pasted patterns
- propose shared abstractions or utilities

### Dead Code

- identify unused functions, classes, and imports
- identify unreachable code paths
- identify unused configuration values

### Large Functions

- identify functions exceeding 60 lines
- propose decomposition strategies

### Large Classes

- identify classes exceeding 300 lines
- propose single-responsibility decomposition

### Cyclomatic Complexity

- identify functions with complexity > 10
- propose simplification strategies

### Deep Nesting

- identify deeply nested logic (> 3 levels)
- propose early returns and guard clauses

---

## Architecture Compliance Scan

### Dependency Direction

Verify dependencies point inward:

```text
API → Application → Domain → Ports → Infrastructure
```

### Forbidden Dependencies

Identify:

- Infrastructure importing Application
- Domain importing FastAPI
- Domain importing SQLAlchemy
- Application importing SQLAlchemy models
- Repositories importing routers
- Routers calling repositories directly
- Services calling database directly

### Layer Violation Detection

- SQL in routers
- Ollama calls in API routes
- Prompt creation in services
- Global database sessions
- ORM models exposed outside repositories
- Domain coupled to infrastructure
- Synchronous I/O in async paths
- `print()` statements

---

## Guardrails Coverage Audit

### AI Output Path Analysis

For every code path that consumes AI-generated content, verify:

- [ ] Guardrails Engine is invoked before persistence/rendering/return
- [ ] Correct guardrail profile is applied (`rewrite_strict` / `analysis_standard` / `validation_paranoid`)
- [ ] `approved`, `repaired`, and `rejected` outcomes are all explicitly handled
- [ ] Rejection raises `GuardrailRejectionError` with violation codes
- [ ] Guardrail audit events are persisted in the same transaction as content

### Missing Guardrails Detection

Identify:

- AI output persisted without guardrail validation
- AI output rendered without guardrail validation
- AI output returned to client without guardrail validation
- Guardrails called conditionally instead of unconditionally
- Ad-hoc validation logic substituted for Guardrails Engine
- Previous guardrail approval carried over to new AI output

---

## Security Scan

### Input Validation

- identify unvalidated external inputs
- identify missing MIME type validation
- identify missing file size checks

### Secret Exposure

- identify hardcoded secrets
- identify secrets in logs
- identify secrets in error messages

### Injection Risks

- identify raw SQL concatenation
- identify unescaped HTML
- identify unescaped LaTeX commands
- identify prompt injection vulnerabilities in retrieval paths

---

## Performance Scan

### Database

- identify N+1 queries
- identify missing indexes
- identify `SELECT *` usage
- identify missing connection pooling

### AI Pipeline

- identify sequential guardrail validators that could run concurrently
- identify duplicate embedding computations
- identify missing caching opportunities
- identify HTTP client recreation (should reuse)

### Application

- identify synchronous I/O in async paths
- identify blocking calls
- identify memory leaks (unclosed resources)

---

# Resolution Phase

## Refactoring Strategies

For each identified issue, propose:

1. **Current state** — what exists and why it's problematic
2. **Target state** — what the code should look like
3. **Migration path** — incremental steps to get there
4. **Risk assessment** — what could break
5. **Test requirements** — tests needed to verify behavior preservation

## Priority Order

1. Security risks (critical)
2. Architecture violations (high)
3. Guardrails coverage gaps (high)
4. Performance issues (medium)
5. Code quality (medium)
6. Documentation gaps (low)

---

# Refactoring Rules

## Forbidden During Refactoring

- changing business behavior without explicit approval
- removing existing tests
- removing existing guardrail validators
- reducing test coverage
- introducing new architecture patterns without ADR
- bypassing Guardrails for "simplicity"

## Required During Refactoring

- all tests pass after every refactoring step
- Ruff, Black, MyPy pass after every step
- guardrail adversarial tests pass with same or better detection rates
- documentation updated for architectural changes
- migration notes for API changes

---

# Database Refactoring

When changing database schema:

1. update ORM models
2. generate Alembic migration
3. review migration for safety
4. test migration (up and down)
5. update repositories
6. verify repositories still reject ungated AI output
7. update documentation

Never manually edit production migrations unless necessary.

---

# API Refactoring

Every API change requires:

- updated request/response models
- updated validation
- updated documentation
- updated tests
- version compatibility check
- guardrail rejection error shape preserved

---

# Guardrails Refactoring

When refactoring guardrail validators:

1. document current detection rates
2. make the change
3. re-run adversarial test suite
4. compare detection rates
5. only accept if rates have not regressed
6. update guardrail documentation

---

# Required Deliverables

## Refactoring Report

Generate a structured report containing:

1. **Executive Summary** — overall codebase health assessment
2. **Architecture Compliance** — violations found and remediation plan
3. **Guardrails Coverage** — gaps found and fixes needed
4. **Security Findings** — vulnerabilities found and mitigations
5. **Performance Findings** — bottlenecks found and optimizations
6. **Code Quality** — issues found and refactoring proposals
7. **Migration Notes** — breaking changes and migration steps
8. **Test Impact** — tests affected and new tests needed

## Code Changes

For each refactoring:

1. modified files with explanations
2. new test files
3. updated documentation
4. migration scripts (if database changes)

---

# Quality Requirements

Refactored code must:

- pass Ruff,
- pass MyPy (strict),
- maintain or improve test coverage,
- maintain or improve guardrail detection rates,
- preserve all existing behavior,
- and be production deployable.

---

# Output Requirements

Return:

1. refactoring report (structured document),
2. prioritized issue list,
3. code changes per issue,
4. migration notes,
5. updated tests,
6. updated documentation,
7. architecture compliance summary,
8. guardrails coverage summary,
9. performance improvement estimates,
10. and any trade-offs made.

Do not introduce new technical debt.

Do not remove existing architecture without justification.

---

# Final Instruction

Perform a **complete production-grade refactoring review** that:

- identifies all architecture violations,
- audits guardrails coverage,
- detects security risks,
- finds performance bottlenecks,
- improves code quality,
- preserves existing behavior,
- maintains test coverage,
- and produces a prioritized remediation plan

for the entire Tailr codebase.

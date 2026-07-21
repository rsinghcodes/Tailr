# Testing — Production Implementation Prompt

## Objective

Implement the complete production-ready **Testing Framework** for Tailr.

This module establishes the testing strategy, infrastructure, and test suites that ensure every component — from deterministic parsing to AI-powered optimization — functions correctly, reliably, and securely.

The Testing Framework is responsible for:

- testing pyramid implementation,
- unit tests for deterministic logic,
- integration tests for infrastructure,
- component tests for services,
- guardrail tests for AI safety,
- adversarial tests for security,
- workflow tests for orchestration,
- evaluation benchmarks for AI quality,
- test fixtures and factories,
- CI/CD integration,
- and coverage enforcement.

No feature is complete without tests.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/testing.md
- rules/security.md
- rules/logging.md
- ADR-0002 — Clean Architecture
- ADR-0010 — Evaluation-Driven Development
- ADR-0011 — Validation & Guardrails Engine
- 17-Testing.md
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Testing Pyramid

```text
         Manual Evaluation
               ▲
       End-to-End Tests
               ▲
        Workflow Tests
               ▲
     Integration Tests
               ▲
  Guardrail & Security Tests
               ▲
       Component Tests
               ▲
         Unit Tests
```

AI evaluations and guardrail evaluations execute alongside workflow tests.

---

# Unit Tests

Verify deterministic business logic.

### Scope

- domain entities and value objects
- domain services
- utility functions
- validators
- parsers (lexer, parser, semantic analyzer)
- normalization logic
- pagination calculations
- exception serialization
- enum values

### Rules

- no I/O
- no database
- no network
- fast execution
- deterministic
- mock infrastructure dependencies

### Coverage Target

**95%+** for domain and shared modules.

---

# Integration Tests

Verify infrastructure interactions.

### Scope

- PostgreSQL repositories (CRUD, soft delete, pagination)
- Redis operations (cache, pub/sub)
- Qdrant vector store (upsert, search, delete)
- Alembic migrations (up, down, idempotency)
- HTTP client instrumentation
- LLM provider connectivity (with mock server)

### Requirements

- use **Testcontainers** for PostgreSQL, Redis, Qdrant
- async fixtures with proper cleanup
- transaction rollback between tests
- realistic data volumes

### Coverage Target

**90%+** for infrastructure modules.

---

# Component Tests

Verify individual services in isolation.

### Scope

- ResumeApplicationService
- JDApplicationService
- WorkflowService
- KnowledgeService
- ATSService
- RenderService

### Requirements

- mock repositories and providers
- verify service orchestration logic
- verify guardrail integration (approved, repaired, rejected paths)
- verify error handling

---

# Guardrail Tests

Verify AI safety enforcement.

### Required Tests

- **Approved Path** — valid AI output passes all validators
- **Repaired Path** — recoverable issues are automatically fixed
- **Rejected Path** — invalid output is rejected with violation codes
- **Hallucination Detection** — fabricated employers, projects, metrics, dates, technologies
- **Prompt Injection** — known injection patterns are detected and blocked
- **Resume Integrity** — immutable facts cannot be altered
- **PII/Secret Scanning** — sensitive data in AI output is detected
- **ATS Validation** — formatting rules are enforced
- **LaTeX Safety** — dangerous commands are detected
- **Malformed JSON** — invalid JSON is handled (repair or reject)

### Adversarial Tests

Include at least:

- known prompt injection patterns ("Ignore previous instructions", "Reveal system prompt")
- hallucination attempts (invented employer, fabricated metric)
- Unicode normalization attacks
- nested injection in retrieved context

### Rules

- never mock the Guardrails Engine in integration or workflow tests unless the test is exclusively about a component upstream of Guardrails
- use real (or realistic adversarial) inputs
- test with real validator implementations

---

# Workflow Tests

Verify end-to-end workflow orchestration.

### Scope

- full workflow execution (happy path)
- individual node execution
- state transitions (valid and invalid)
- guardrails at every generation step
- retry behavior (success after retry, exhausted retries)
- checkpoint persistence and recovery
- cancellation
- streaming progress events
- human approval flow
- timeout handling

### Requirements

- mock LLM providers with deterministic responses
- use real guardrail validators
- verify event emission
- verify telemetry

---

# API Tests

Verify HTTP layer behavior.

### Scope

- every endpoint (success and failure paths)
- request validation
- response model serialization
- authentication (valid, expired, missing token)
- authorization (owner, non-owner)
- pagination
- rate limiting
- health endpoints
- guardrail rejection error responses
- OpenAPI schema generation

### Requirements

- use `httpx.AsyncClient`
- mock application services
- never mock business logic

---

# Evaluation Tests (EDD)

Verify AI output quality as defined in ADR-0010.

### Metrics

- hallucination rate
- guardrail pass rate
- guardrail repair rate
- guardrail rejection rate
- retrieval precision@K
- retrieval recall@K
- MRR, NDCG
- ATS score improvement
- keyword coverage improvement
- prompt injection detection rate

### Requirements

- golden test datasets (resume + JD → expected output)
- regression detection for guardrail effectiveness
- evaluation results stored for trend analysis
- a prompt version with a rising rejection rate is a regression signal

---

# Test Fixtures & Factories

### Fixtures

- database session (async, with rollback)
- Redis client
- Qdrant client
- mock LLM provider
- mock HTTP server
- sample resume (canonical model)
- sample job description
- sample workflow state
- guardrail result (approved, repaired, rejected)

### Factories

Use factory pattern for test data generation:

- `ResumeFactory`
- `JobDescriptionFactory`
- `ExperienceFactory`
- `ProjectFactory`
- `WorkflowStateFactory`
- `GuardrailResultFactory`

---

# Test Configuration

### conftest.py

- shared fixtures at project root
- module-specific fixtures in each test directory
- event loop configuration for pytest-asyncio
- Testcontainers lifecycle management

### Environment

- `APP_ENV=testing`
- minimal log noise
- deterministic timestamps where possible
- capture logs for assertions

---

# CI/CD Integration

### Required CI Steps

```text
1. Ruff (linting)
2. Black (formatting)
3. MyPy (type checking)
4. Pytest (unit tests)
5. Pytest (integration tests with Testcontainers)
6. Pytest (guardrail tests)
7. Coverage report (enforce minimums)
8. Evaluation suite (if AI-related changes)
```

### Coverage Enforcement

| Module          | Minimum |
| --------------- | ------- |
| Domain          | 95%     |
| Shared          | 95%     |
| Application     | 90%     |
| Infrastructure  | 90%     |
| API             | 85%     |
| Agents          | 90%     |
| Workflows       | 90%     |
| Guardrails      | 95%     |
| Parser          | 95%     |
| RAG             | 90%     |

---

# Required File Structure

```text
tests/
├── conftest.py
├── factories/
│   ├── __init__.py
│   ├── resume.py
│   ├── job.py
│   ├── workflow.py
│   └── guardrail.py
├── fixtures/
│   ├── __init__.py
│   ├── database.py
│   ├── redis.py
│   ├── qdrant.py
│   ├── providers.py
│   └── data/
│       ├── sample_resume.tex
│       ├── sample_resume.json
│       ├── sample_jd.txt
│       └── adversarial/
│           ├── injection_patterns.json
│           └── hallucination_cases.json
├── unit/
│   ├── domain/
│   ├── shared/
│   ├── parsers/
│   └── utils/
├── integration/
│   ├── repositories/
│   ├── providers/
│   ├── vectorstore/
│   └── migrations/
├── component/
│   ├── services/
│   └── agents/
├── guardrail/
│   ├── test_schema_validator.py
│   ├── test_hallucination_detector.py
│   ├── test_prompt_injection.py
│   ├── test_integrity_validator.py
│   ├── test_pii_scanner.py
│   ├── test_ats_validator.py
│   ├── test_latex_safety.py
│   └── test_adversarial.py
├── workflow/
│   ├── test_full_workflow.py
│   ├── test_nodes.py
│   ├── test_retry.py
│   └── test_checkpointing.py
├── api/
│   ├── test_resume_router.py
│   ├── test_job_router.py
│   ├── test_workflow_router.py
│   └── test_health_router.py
└── evaluation/
    ├── test_retrieval_quality.py
    ├── test_generation_quality.py
    └── test_guardrail_effectiveness.py
```

---

# Quality Requirements

Generated test code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- be deterministic,
- be repeatable,
- have no test interdependencies,
- use proper async patterns,
- and clean up all resources.

---

# Output Requirements

Return:

1. complete test framework setup (conftest, factories, fixtures),
2. sample test files for each test category,
3. CI pipeline configuration (GitHub Actions),
4. coverage configuration (pyproject.toml),
5. testing strategy documentation,
6. adversarial test case documentation,
7. evaluation benchmark documentation,
8. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Testing Framework** that provides:

- comprehensive test pyramid,
- guardrail safety testing,
- adversarial security testing,
- evaluation-driven AI testing,
- CI/CD integration,
- coverage enforcement,
- reusable fixtures and factories,
- and deterministic test execution

for the entire Tailr platform.

# Testing Strategy

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the testing strategy for Tailr.

The objective is to ensure that every component of the platform—from resume parsing to AI-powered optimization—functions correctly, reliably, and securely.

Unlike traditional software, Tailr requires testing of deterministic code, AI agents, prompt behavior, retrieval quality, workflow orchestration, and user experience.

Testing is integrated throughout the Software Development Lifecycle (SDLC) and Continuous Integration/Continuous Deployment (CI/CD) pipeline.

---

# 2. Testing Goals

The testing strategy aims to:

- Verify business correctness
- Prevent regressions
- Validate AI behavior
- Detect hallucinations
- Ensure prompt reliability
- Measure retrieval quality
- Validate guardrail enforcement
- Protect against security vulnerabilities
- Guarantee production readiness

---

# 3. Testing Philosophy

Tailr follows six testing principles.

## Test Early

Every component is tested during development.

---

## Test Automatically

All repeatable tests run automatically in CI.

---

## Test Deterministic Components First

Business logic should never depend on LLM behavior.

---

## AI Requires Evaluation

AI outputs are evaluated instead of compared literally.

---

## Prevent Regression

Every bug becomes a permanent test case.

---

## Production Monitoring Complements Testing

Observability validates assumptions after deployment.

---

# 4. Testing Pyramid

```
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

# 5. Unit Testing

Unit tests verify deterministic business logic.

Examples

- Resume Parser
- Validation Engine
- ATS Calculator
- Prompt Builder
- Data Models
- Utility Functions
- Guardrail validators
- JSON schema validators
- Prompt injection detector

Framework

```
pytest
```

Coverage Target

> 90%

---

# 6. Component Testing

Each subsystem is tested independently.

Examples

Parser
Retriever
Planner
Rewriter
Guardrails
Validator
Renderer

No external dependencies are required.

---

# 7. Integration Testing

Verify interactions between services.

Examples

FastAPI ↔ PostgreSQL
FastAPI ↔ Redis
FastAPI ↔ Qdrant
Workflow ↔ Ollama
Parser ↔ Knowledge Builder
Workflow ↔ Guardrails
Guardrails ↔ Validation Engine
Guardrails ↔ Langfuse telemetry

Framework

```
pytest

Docker Compose
```

---

# 8. Workflow Testing

Entire AI workflows are executed.

```
Resume

↓

Parser

↓

Knowledge Builder

↓

Retriever

↓

Planner

↓

Rewriter

↓

Guardrails

↓

Validator

↓

ATS

↓

Renderer
```

The workflow must complete successfully and all guardrail checks must pass or be repaired.

---

# 9. API Testing

Every REST endpoint is tested.

Verify

- JSON schema validation
- Structured output validation
- Business rules
- Hallucination detection
- Prompt injection detection
- PII detection
- Keyword validation
- Formatting validation
- Output repair behavior
- Retry behavior

Validation and guardrail behavior must remain deterministic.

Framework

```
pytest

httpx
```

---

# 10. Parser Testing

Parser tests include

- Valid LaTeX
- Invalid LaTeX
- Unsupported templates
- Empty sections
- Nested commands
- Source mapping
- Canonical model generation

Golden files verify parser stability.

---

# 11. Validation Engine Testing

Verify

- Schema validation
- Business rules
- Hallucination detection
- Keyword validation
- Formatting validation
- Retry behavior

Validation must remain deterministic.

---

# 12. RAG Testing

Evaluate retrieval quality.

Metrics

- Recall@K
- Precision@K
- Mean Reciprocal Rank (MRR)
- Context relevance
- Chunk quality

Poor retrieval should fail evaluation.

---

# 13. Prompt Testing

Each prompt version is tested.

Verify

- JSON validity
- Schema compliance
- Instruction following
- Prompt injection resistance
- Prompt leakage resistance
- Hallucination rate
- Latency
- Token usage

Prompt versions are regression tested.

---

# 14. LLM Evaluation

LLM responses are evaluated using

Reference outputs

↓

Semantic similarity

↓

Rule validation

↓

Human review (selected cases)

Exact string matching is avoided.

---

# 15. Agent Testing

Every agent is tested independently.

Examples

JD Analyzer

Planner

Rewriter

ATS Advisor

Each agent receives predefined inputs and expected structured outputs. Agent outputs must pass guardrail validation before being considered successful.

---

# 16. Guardrail Testing

Guardrail testing verifies AI safety enforcement independently of business logic.

Required test suites

- JSON validation
- Prompt injection detection
- Prompt leakage detection
- Hallucination detection
- Resume integrity validation
- ATS formatting validation
- PII detection
- Toxicity detection
- Output repair validation
- Guardrail timeout handling
- Guardrail retry behavior

Example test categories

```text
tests/guardrails/
  test_json_validator.py
  test_prompt_injection.py
  test_hallucination.py
  test_pii.py
  test_resume_integrity.py
  test_output_repair.py
```

Guardrail tests must execute in CI for every pull request.

---

# 17. Golden Dataset

Tailr maintains a benchmark dataset.

Contents

- Sample resumes
- Job descriptions
- Expected ATS scores
- Expected rewrite plans
- Expected parser outputs
- Known prompt injection samples
- Known hallucination examples
- Expected guardrail decisions
- Expected repair outcomes

Changes are evaluated against this dataset before release. The dataset must contain both valid and intentionally malicious samples.

---

# 18. Regression Testing

Every resolved bug becomes a regression test.

Regression suite runs on every pull request.

No previously fixed issue should reappear.

Security incidents and guardrail bypasses also become permanent regression tests.

---

# 19. Performance Testing

Measure

- API latency
- Parser speed
- Embedding generation
- Vector search
- Workflow duration
- PDF generation

Framework

```
Locust

k6
```

Performance targets are defined in deployment documents.

---

# 20. Load Testing

Simulate

- Concurrent users
- Parallel workflows
- Bulk resume uploads
- Simultaneous ATS analysis

The system should degrade gracefully under load.

---

# 21. Security Testing

Security verification includes

- Authentication
- Authorization
- SQL Injection
- Prompt Injection
- Prompt Leakage
- Hallucination Bypass
- XSS
- File Upload Validation
- Rate Limiting
- Dependency Scanning
- Guardrail Bypass Attempts
- PII Leakage Detection

Security and guardrail tests run automatically in CI.

---

# 22. Chaos Testing

Introduce controlled failures.

Examples

- Redis unavailable
- Qdrant offline
- Ollama timeout
- PostgreSQL restart

Workflows should recover gracefully.

---

# 23. End-to-End Testing

User scenario

```
Upload Resume

↓

Upload JD

↓

Optimize

↓

Guardrails

↓

Review Suggestions

↓

Generate PDF

↓

Download Resume
```

Entire user journeys are validated. End-to-end tests verify that unsafe AI outputs are blocked before reaching the user.

Framework

```
Playwright
```

---

# 24. Manual QA

Manual evaluation focuses on

- Resume quality
- ATS recommendations
- Prompt improvements
- UX
- Generated PDFs

Human review complements automated testing.

---

# 25. Continuous Integration

GitHub Actions pipeline

```
Checkout

↓

Lint

↓

Type Check

↓

Unit Tests

↓

Guardrail Tests

↓

Integration Tests

↓

AI Evaluations

↓

Security Scan

↓

Docker Build

↓

Deploy
```

Deployment occurs only if all required stages pass.

---

# 26. Test Data Management

Test datasets include

- Synthetic resumes
- Anonymous job descriptions
- Mock user accounts
- Benchmark prompts
- Prompt injection samples
- Hallucination samples
- PII leakage samples
- Guardrail benchmark cases

No real user resumes are used in automated testing.

---

# 27. Coverage Goals

| Component         | Target |
| ----------------- | ------ |
| Business Logic    | 95%    |
| API               | 90%    |
| Parser            | 95%    |
| Guardrails        | 95%    |
| Validation Engine | 95%    |
| Workflow          | 90%    |
| Frontend          | 80%    |

Coverage complements—not replaces—quality evaluation.

---

# 28. AI Evaluation Metrics

Track

- Hallucination rate
- JSON validity
- Guardrail pass rate
- Guardrail repair rate
- Prompt injection detection rate
- Validation pass rate
- Prompt success rate
- Retrieval accuracy
- User acceptance rate
- ATS improvement
- Rewrite acceptance

These metrics are monitored continuously and compared across model versions and prompt versions.

---

# 29. Future Enhancements

Planned capabilities

- Self-healing test generation
- AI-generated regression tests
- Multi-model benchmarking
- Prompt A/B testing
- Automatic benchmark expansion
- Continuous offline evaluation
- Automated guardrail fuzzing
- Adversarial prompt generation
- Continuous red-team evaluation
- Guardrail effectiveness scoring
- AI safety benchmark automation

---

# 30. Architecture Decisions

| Decision             | Rationale                                |
| -------------------- | ---------------------------------------- |
| pytest               | Mature Python testing ecosystem          |
| Playwright           | Reliable browser automation              |
| Golden datasets      | Stable AI regression testing             |
| AI evaluation layer  | Measures quality beyond correctness      |
| Guardrail test suite | Validates AI safety policies             |
| Adversarial testing  | Detects prompt injection vulnerabilities |
| Docker Compose       | Consistent integration environment       |
| CI-first testing     | Prevent regressions before deployment    |

---

# 31. Summary

Tailr adopts a comprehensive multi-layer testing strategy that combines traditional software testing with AI-specific evaluation and guardrail validation techniques.

By testing deterministic components, AI agents, prompts, retrieval pipelines, guardrail policies, workflows, APIs, and user journeys independently, the platform achieves high reliability while accommodating the probabilistic nature of LLM-based systems.

The dedicated guardrail test suite ensures that prompt injection attempts, hallucinated resume content, malformed structured outputs, PII leakage, and other AI-specific risks are detected before deployment.

This strategy ensures that every release is functionally correct, operationally stable, security-hardened, and capable of delivering consistent, safe, and high-quality resume optimizations.

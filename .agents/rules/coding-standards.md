---
trigger: always_on
---

# Purpose

This document defines the official coding standards for Tailr. Every AI coding agent must follow these standards. Every Pull Request will be reviewed against this document. When standards conflict with personal preferences, this document always wins.

# Philosophy

Code is read far more often than it is written. Optimize for readability, maintainability, and correctness. Never optimize for writing fewer lines. AI-generated output is never trusted by default. Code that consumes AI output is held to the same rigor as code that consumes untrusted external input.

# Python Version

Python 3.13. Do not write compatibility code for older versions. Use modern Python features whenever they improve clarity:
- `match` statements
- `|` union types
- `pathlib`
- `dataclasses` when appropriate
- `StrEnum`
- `slots`

# Formatting

Formatting is automatic. Never manually align code.
Tools: Ruff, Black, isort (via Ruff).

# Line Length

Maximum: 88 characters. Exceptions only when readability improves.

# Naming

## Variables
- **Good:** `resume_id`, `job_description`, `embedding_model`, `guardrail_result`
- **Bad:** `x`, `temp`, `obj`, `data1`

## Functions
Use verbs.
- **Good:** `calculate_score()`, `generate_embeddings()`, `validate_resume()`, `parse_document()`, `run_guardrails()`
- **Bad:** `score()`, `process()`, `handle()`

## Classes
Use nouns.
- **Good:** `ResumeService`, `JobAnalyzer`, `ResumeRepository`, `EmbeddingProvider`, `GuardrailsEngine`, `HallucinationDetector`
- **Bad:** `Manager`, `Utils`, `Helper`, `Processor`

## Constants
UPPER_CASE: `MAX_FILE_SIZE`, `DEFAULT_TIMEOUT`, `VECTOR_DIMENSION`, `GUARDRAIL_DEFAULT_PROFILE`

## Modules
`snake_case.py`. Never CamelCase filenames.

# Imports

Order:
1. Standard Library
2. Third Party
3. Internal

Separate groups with one blank line. Never use wildcard imports.
- **Bad:** `from utils import *`
- **Good:** `from utils.parser import ResumeParser`

# Type Hints

Every public function must have type hints. Return types are mandatory.
- **Bad:** `def create(data):`
- **Good:** `def create(data: ResumeRequest) -> Resume:`

Guardrail results must never be typed as `dict` or `Any`. Use the typed `GuardrailResult` model (`status`, `repair_applied`, `violations`, `warnings`, `metadata`) so callers cannot forget to check `status`.

# Docstrings

Public classes, public functions, and public modules must have Google Style docstrings.

```python
def generate_embeddings(text: str) -> list[float]:
    """Generate embeddings.

    Args:
        text: Input text.

    Returns:
        Vector embedding.
    """
```

A guardrail validator's docstring must state what it detects and what it does NOT detect, so reviewers can reason about coverage gaps.

```python
def detect_hallucination(
    generated: str, canonical_resume: CanonicalResume
) -> GuardrailResult:
    """Detect content not grounded in the canonical resume.

    Flags invented employers, projects, technologies, dates, and metrics.
    Does not evaluate tone, grammar, or ATS formatting — see `ats_validator.py`.

    Args:
        generated: Raw text produced by the Rewrite Agent.
        canonical_resume: The user's source-of-truth resume model.

    Returns:
        GuardrailResult with status approved/repaired/rejected.
    """
```

# Function Rules

- Maximum length: 60 lines
- Maximum parameters: 5
- Maximum nesting: 3
- Prefer early return.

```python
# Good
if not a:
    return
if not b:
    return
```

Guardrail validators follow the same limits. A validator that grows past 60 lines must be split into single-purpose validators registered in the same pipeline.

# Class Rules

- Maximum: 300 lines
- Single responsibility. If a class has multiple responsibilities, split it.
- A single guardrail validator class must implement exactly one check (e.g. `PromptInjectionDetector` only detects injection patterns; it must not also do PII scanning). Composition happens in the `GuardrailsEngine` pipeline.

# Comments

Comment WHY, never comment WHAT.

```python
# Retry to handle transient provider failures
# rewrite_strict is required here because this output is written directly into the resume model
result = await guardrails.run(output, profile="rewrite_strict")
```

# Async

Backend is async-first across Database, HTTP, Redis, LLM, and Guardrails. Never block the event loop.
Independent validators inside the Guardrails pipeline should run concurrently (`asyncio.gather`) where they have no data dependency on each other, keeping latency low.

- **Forbidden:** `requests`, `time.sleep`, `subprocess.run()`
- **Allowed:** `httpx.AsyncClient`, `asyncio.sleep()`

# Error Handling

Never catch `Exception` unless re-raising.
- **Good:** `except ValidationError:`, `except ProviderError:`, `except DatabaseError:`, `except GuardrailRejectionError:`

A `GuardrailRejectionError` must never be caught and discarded. It may only be caught to translate it into a structured API error or a workflow `Failed` state. Never catch it purely to allow execution to continue with rejected content.

# Exceptions

Use typed exceptions per layer. Never raise `RuntimeError` or generic `Exception`.
Guardrails-specific exceptions must carry structured detail.

```python
raise GuardrailRejectionError(
    violation_codes=["hallucinated_technology"],
    section="projects",
    guardrail_profile="rewrite_strict",
)
```

# Logging

Never use `print()`. Always use `logging.getLogger(__name__)` with structured logging.

```python
logger.info(
    "Guardrails completed",
    extra={
        "workflow_id": workflow_id,
        "guardrail_profile": profile,
        "status": result.status,
        "violation_codes": result.violations,
        "repair_applied": result.repair_applied,
        "duration_ms": duration,
    },
)
```

Never log full resume content or job description text at INFO level or above. Treat resume content as sensitive.

# Configuration

Never hardcode values. Use Settings.
- **Good:** `timeout = settings.HTTP_TIMEOUT`
- **Good:** `profile = settings.GUARDRAIL_PROFILES["rewrite"]`

Guardrail thresholds, enabled validators, and profile-to-task mappings live in configuration, never as inline conditionals across services.

# FastAPI

Routes must be thin: `Router → Application Service → Repository`.
Guardrails must never be invoked inside a router. It is always invoked by the Application Service owning the use case, immediately after the provider call.

# Dependency Injection

Never instantiate services manually. Use `Depends(get_resume_service)`.
Inject `GuardrailsEngine` into the service; never instantiate individual validators ad hoc inside business logic.

# SQLAlchemy

Use SQLAlchemy 2.x style with async sessions. Never use `session.query()`. Use `select()`. Never expose ORM models outside repositories.

# Pydantic

Use Pydantic v2. Separate Request, Response, and Internal schemas. Do not reuse request models as database models.
`GuardrailResult` and its violation types are Pydantic v2 models. Never represent a guardrail outcome as a raw `dict`.

# Repositories

Repositories only persist data. Forbidden: Validation, AI, Business rules, Prompt generation.
Persisting AI-generated content whose `GuardrailResult.status` is not `approved` or `repaired` is prohibited. Repository signatures should accept an `ApprovedResumeContent` type that can only be constructed after a successful guardrail check.

# Services

Services coordinate work: validate business rules, call repositories, call providers, call the `GuardrailsEngine` on every AI-generated output before anything else, and return domain objects.

# Providers

Providers communicate with external systems (Ollama, OpenAI, Qdrant, Redis, S3). Providers never contain business or guardrail logic; their only job is returning raw model responses.

# AI Prompts

Prompt templates belong in `prompts/`. Never inline prompts. Every prompt requires versioning and a guardrail profile reference in its metadata (e.g. `guardrail_profile: rewrite_strict`).

# AI Output

Never trust LLM output. Always validate.
"Validate" means: run through Guardrails Engine first (schema, JSON, prompt injection, hallucination, integrity, PII, ATS, LaTeX safety), then business `validators/`.
A malformed-JSON or schema failure must first go through the Guardrails Repair Engine before escalating to an LLM retry.

# RAG

Pipeline stages must remain separate:
`Parser → Chunker → Embedding → Retriever → Reranker → Guardrails Injection Scan → Prompt Builder → Generator → Guardrails Output Validation → Validator`

Retrieved chunks are untrusted text. Scan them for injection patterns before interpolating into a prompt.

# Testing

Every feature requires Unit, Integration, Edge Case, Failure, and Regression tests.
Every guardrail validator additionally requires:
1. Positive test (approves valid content)
2. Targeted negative test (rejects target issue)
3. Adversarial test (known attack pattern / prompt injection / hallucinated tech)
4. Regression test for any past production bug

Never mock the `GuardrailsEngine` in tests verifying end-to-end AI safety behavior.

# Performance

Avoid N+1 queries, reuse clients, cache expensive operations, batch embeddings, use pagination.
Independent guardrail validators should execute concurrently (`asyncio.gather`) where data dependencies allow.

# Security

Validate uploads, MIME types, file sizes. Escape HTML, protect secrets, never log credentials or stack traces.
PII/secret scanning is delegated to Guardrails Engine. LaTeX safety validation blocks dangerous commands (`\input`, `\include`, `\write18`, `\openout`, `\catcode`).

# Code Smells

Avoid: God Classes, Utility Classes, Global State, Circular Imports, Duplicate Logic, Deep Nesting, Long Functions, Magic Numbers, Hardcoded Strings.
Forbidden: AI output consumed without a preceding Guardrails call, `try/except` swallowing guardrail rejections, or validators mixing safety and business rules.

# Refactoring

Refactor when readability, complexity, or architecture improves.
Refactoring guardrail validators requires an evaluation run proving detection rates have not regressed.

# Definition of Clean Code

A module is clean when it has one responsibility, is typed, documented, testable, handles failures correctly, and (if consuming AI output) invokes Guardrails and correctly branches on `approved`/`repaired`/`rejected`.

# Before Every Commit

Run: `ruff check .`, `ruff format .`, `mypy .`, `pytest`. Fix all warnings. If modifying validators or prompts, run the guardrail adversarial test suite.

# Final Rule

Write code that another senior engineer can understand in five minutes. Code that quietly bypasses Guardrails is broken code.

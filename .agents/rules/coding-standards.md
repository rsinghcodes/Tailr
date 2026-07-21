# Coding Standards

> Project: Tailr
> Version: 1.0
> Status: Production

---

# Purpose

This document defines the official coding standards for Tailr.

Every AI coding agent must follow these standards.

Every Pull Request will be reviewed against this document.

When standards conflict with personal preferences,
this document always wins.

---

# Philosophy

Code is read far more often than it is written.

Optimize for readability.

Optimize for maintainability.

Optimize for correctness.

Never optimize for writing fewer lines.

AI-generated output is never trusted by default. Code that consumes AI output is held to the same rigor as code that consumes untrusted external input.

---

# Python Version

Python 3.13

Do not write compatibility code for older versions.

Use modern Python features whenever they improve clarity.

Examples:

✓ match statements

✓ | union types

✓ pathlib

✓ dataclasses when appropriate

✓ StrEnum

✓ slots

---

# Formatting

Formatting is automatic.

Never manually align code.

Tools:

Ruff

Black

isort (via Ruff)

---

# Line Length

Maximum:

88 characters

Exceptions only when readability improves.

---

# Naming

## Variables

Good

resume_id

job_description

embedding_model

guardrail_result

Bad

x

temp

obj

data1

---

## Functions

Use verbs.

Good

calculate_score()

generate_embeddings()

validate_resume()

parse_document()

run_guardrails()

---

Bad

score()

process()

handle()

---

## Classes

Use nouns.

Good

ResumeService

JobAnalyzer

ResumeRepository

EmbeddingProvider

GuardrailsEngine

HallucinationDetector

Bad

Manager

Utils

Helper

Processor

---

## Constants

UPPER_CASE

MAX_FILE_SIZE

DEFAULT_TIMEOUT

VECTOR_DIMENSION

GUARDRAIL_DEFAULT_PROFILE

---

## Modules

snake_case.py

Never CamelCase filenames.

---

# Imports

Order

Standard Library

↓

Third Party

↓

Internal

Separate groups with one blank line.

Never use wildcard imports.

Bad

from utils import \*

Good

from utils.parser import ResumeParser

---

# Type Hints

Every public function must have type hints.

Bad

def create(data):

Good

def create(data: ResumeRequest) -> Resume:

Return types are mandatory.

Guardrail results must never be typed as `dict` or `Any`. Use the typed `GuardrailResult` model (`status`, `repair_applied`, `violations`, `warnings`, `metadata`) so callers cannot forget to check `status`.

---

# Docstrings

Public classes

Public functions

Public modules

must have docstrings.

Use Google Style.

Example

def generate_embeddings(text: str) -> list[float]:
"""
Generate embeddings.

    Args:
        text:
            Input text.

    Returns:
        Vector embedding.
    """

A guardrail validator's docstring must state what it detects and what it does NOT detect, so reviewers can reason about coverage gaps.

Example

def detect_hallucination(
generated: str, canonical_resume: CanonicalResume
) -> GuardrailResult:
"""
Detect content not grounded in the canonical resume.

    Flags invented employers, projects, technologies, dates,
    and metrics. Does not evaluate tone, grammar, or ATS
    formatting — see `ats_validator.py` for those checks.

    Args:
        generated:
            Raw text produced by the Rewrite Agent.
        canonical_resume:
            The user's source-of-truth resume model.

    Returns:
        GuardrailResult with status approved/repaired/rejected.
    """

---

# Function Rules

Maximum length

60 lines

Maximum parameters

5

Maximum nesting

3

Prefer early return.

Bad

if a:

    if b:

        if c:

Good

if not a:

    return

if not b:

    return

Guardrail validators follow the same limits. A validator that grows past 60 lines is a signal it is checking more than one thing and should be split into two validators registered in the same pipeline.

---

# Class Rules

Maximum

300 lines

Single responsibility.

If class has multiple responsibilities,

split it.

A single guardrail validator class must implement exactly one check (e.g. `PromptInjectionDetector` only detects injection patterns; it must not also do PII scanning). Composition happens in the `GuardrailsEngine` pipeline, not inside one large validator class.

---

# Comments

Comment WHY.

Never comment WHAT.

Bad

# increment i

i += 1

Good

# Retry to handle transient provider failures

Good

# rewrite_strict is required here because this output

# is written directly into the resume model

result = await guardrails.run(output, profile="rewrite_strict")

---

# Async

Backend is async-first.

Database

Async

HTTP

Async

Redis

Async

LLM

Async

Guardrails

Async

Never block the event loop.

Independent validators inside the Guardrails pipeline should run concurrently (`asyncio.gather`) where they have no data dependency on each other, to keep guardrail latency low.

Forbidden

requests

time.sleep

subprocess.run()

Allowed

httpx.AsyncClient

asyncio.sleep()

---

# Error Handling

Never catch Exception unless re-raising.

Bad

except Exception:

Good

except ValidationError:

except ProviderError:

except DatabaseError:

except GuardrailRejectionError:

A `GuardrailRejectionError` must never be caught and discarded. It may only be caught to translate it into a structured API error or a workflow `Failed` state. Never catch it purely to allow execution to continue with the rejected content.

---

# Exceptions

Use typed exceptions.

Every layer has its own exception types.

Never raise RuntimeError.

Never raise generic Exception.

Guardrails-specific exceptions must carry structured detail, not just a message string.

Bad

raise Exception("bad output")

Good

raise GuardrailRejectionError(
violation_codes=["hallucinated_technology"],
section="projects",
guardrail_profile="rewrite_strict",
)

---

# Logging

Never use print().

Always use

logging.getLogger(**name**)

Use structured logging.

Every log should contain useful context.

Bad

logger.info("Done")

Good

logger.info(

    "Resume parsed",

    extra={

        "resume_id": resume.id,

        "duration_ms": duration,

    },

)

Every guardrail run must log its outcome with structured context. Never log the fact that a check ran without logging its result.

Good

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

Never log full resume content or full job description text at INFO level or above. Log identifiers and metadata; treat resume content as sensitive, matching the PII-protection intent of the Guardrails layer itself.

---

# Configuration

Never hardcode values.

Use Settings.

Bad

timeout = 30

Good

timeout = settings.HTTP_TIMEOUT

Bad

if section == "projects":
strict = True

Good

profile = settings.GUARDRAIL_PROFILES["rewrite"]

Guardrail thresholds, enabled validators, and profile-to-task mappings live in configuration, never as inline conditionals scattered across services.

---

# FastAPI

Routes must be thin.

Good

Router

↓

Application Service

↓

Repository

Bad

Router

↓

SQLAlchemy

↓

LLM

↓

Redis

Guardrails must never be invoked from inside a router. It is always invoked by the Application Service that owns the use case, immediately after the provider call that produced the AI output.

---

# Dependency Injection

Never instantiate services manually.

Bad

service = ResumeService()

Good

Depends(get_resume_service)

Bad

result = HallucinationDetector().check(output)

Good

Inject `GuardrailsEngine` into the service; never instantiate individual validators ad hoc inside business logic.

---

# SQLAlchemy

Always use SQLAlchemy 2.x style.

Use async sessions.

Never use session.query().

Use select().

Never expose ORM models outside repositories.

---

# Pydantic

Use Pydantic v2.

Separate:

Request

Response

Internal

schemas.

Do not reuse request models as database models.

`GuardrailResult` and its violation types are Pydantic v2 models like everything else that crosses a boundary. Never represent a guardrail outcome as a raw `dict`.

---

# Repositories

Repositories only persist data.

Forbidden

Validation

AI

Business rules

Prompt generation

Persisting AI-generated content whose `GuardrailResult.status` is not `approved` or `repaired`

If a repository method accepts AI-generated content, its signature should make an ungated value structurally impossible to pass — e.g. accept an `ApprovedResumeContent` type that can only be constructed after a successful guardrail check, rather than accepting a bare `str`.

---

# Services

Services coordinate work.

They should:

Validate business rules.

Call repositories.

Call providers.

Call the Guardrails Engine on every provider response that returns AI-generated content, before doing anything else with it.

Return domain objects.

---

# Providers

Providers communicate with external systems.

Examples

Ollama

OpenAI

Qdrant

Redis

S3

Providers never contain business logic.

Providers never contain guardrail logic. A provider's only job is to return the raw model response; it is the caller's responsibility to run that response through Guardrails. Do not add "safety" shortcuts inside a provider implementation.

---

# AI Prompts

Prompt templates belong in

prompts/

Never inline prompts.

Every prompt requires versioning.

Every prompt references a guardrail profile in its metadata (e.g. `guardrail_profile: rewrite_strict`). A new prompt version must not go to production without a guardrail profile assigned.

---

# AI Output

Never trust LLM output.

Always validate.

Retry when appropriate.

Handle malformed JSON.

Use structured outputs whenever possible.

"Validate" means: run it through the Guardrails Engine first (schema, JSON, prompt injection, hallucination, integrity, PII, ATS, LaTeX safety), then through business `validators/`. These are two distinct, sequential steps — do not conflate a Guardrails pass with full business validation, and do not skip straight to business validation.

A malformed-JSON or schema failure should first go through the Guardrails Repair Engine. Only escalate to a retry against the LLM if repair is not possible.

---

# RAG

Every stage separated.

Parser

↓

Chunker

↓

Embedding

↓

Retriever

↓

Reranker

↓

Guardrails (prompt-injection scan on retrieved context)

↓

Prompt Builder

↓

Generator

↓

Guardrails (full validation of generated output)

↓

Validator

Never combine stages.

Retrieved chunks are untrusted text pulled from documents the user or a third party supplied (job descriptions, career guides). Scan them for injection patterns before they are interpolated into a prompt — do not assume retrieval implies trust.

---

# Testing

Every feature requires

Unit Tests

Integration Tests

Edge Cases

Failure Cases

Regression Tests

No exceptions.

Every guardrail validator additionally requires:

A positive test proving it approves valid content

A negative test proving it rejects the specific issue it targets

At least one adversarial test using a known attack pattern (e.g. a documented prompt-injection phrase, a fabricated technology not present in the source resume)

A regression test for every guardrail bug ever found in production

Never mock the Guardrails Engine in a test that is meant to verify end-to-end AI-safety behavior. Mocking is acceptable only in tests that are explicitly about a different layer.

---

# Performance

Avoid N+1 queries.

Reuse clients.

Cache expensive operations.

Batch embeddings.

Use pagination.

Never load unnecessary data.

Independent guardrail validators should execute concurrently rather than sequentially where they don't depend on each other's output, to keep guardrail overhead low relative to the LLM call itself.

---

# Security

Validate uploads.

Validate MIME types.

Validate file size.

Escape HTML.

Protect secrets.

Never log credentials.

Never expose stack traces.

PII and secret scanning of AI-generated output is handled by the Guardrails Engine's PII/Secret Scanner — do not implement a second, separate PII regex ad hoc inside a service.

Prompt-injection defenses (input scanning, instruction isolation) are implemented inside Guardrails, not reinvented per-agent.

---

# Code Smells

Avoid

God Classes

Utility Classes

Global State

Circular Imports

Duplicate Logic

Deep Nesting

Long Functions

Magic Numbers

Hardcoded Strings

AI output consumed without a preceding Guardrails call

A `try/except` around a Guardrails call whose `except` branch silently proceeds as if the content were approved

A guardrail validator that also performs business validation (mixing the two concerns)

---

# Refactoring

Refactor when

Readability improves

Complexity decreases

Architecture improves

Do not refactor purely for style.

Refactoring guardrail validators requires an accompanying evaluation run (see Evaluation-Driven Development) proving the change does not regress detection rates. Do not refactor a validator and skip re-running its adversarial test suite.

---

# Definition of Clean Code

A module is clean when

It has one responsibility.

It is independently testable.

It is typed.

It is documented.

It follows architecture.

It contains no duplication.

It contains no dead code.

It contains meaningful logs.

It handles failures correctly.

If the module consumes AI output, it invokes Guardrails and correctly branches on `approved` / `repaired` / `rejected`.

---

# Before Every Commit

Run

ruff check .

ruff format .

mypy .

pytest

Fix every warning.

Do not ignore issues.

If the change touches a guardrail validator, prompt, or AI-output-consuming code path, also run the guardrail adversarial test suite before committing.

---

# Final Rule

Write code that another senior engineer
can understand in five minutes.

If that is not possible, rewrite it.

Code that quietly bypasses Guardrails is not fast code — it is broken code. Treat a missing guardrail check with the same severity as a missing type hint on a public function: it does not pass review.

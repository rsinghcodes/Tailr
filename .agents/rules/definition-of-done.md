# Definition of Done (DoD)

> Project: Tailr
> Version: 1.0

---

# Purpose

This document defines the minimum quality requirements before any task,
feature, bug fix, refactor, or architectural change can be considered complete.

If every requirement is not satisfied, the task is NOT DONE.

A task that touches AI-generated content is not done merely because it works.
It is not done until that content has been proven to pass through the
Guardrails Engine before it is persisted, validated, or rendered.

---

# General Requirements

The implementation:

✓ Solves the requested problem

✓ Matches the approved architecture

✓ Compiles successfully

✓ Contains no placeholder code

✓ Contains no TODO comments

✓ Contains no FIXMEs

✓ Contains no dead code

✓ Contains no debug code

✓ Contains no print() statements

✓ Contains no AI-output-consuming code path that skips the Guardrails Engine

---

# Architecture

The implementation:

✓ Respects Hexagonal Architecture

✓ Respects Domain Driven Design

✓ Uses dependency injection

✓ Does not introduce circular dependencies

✓ Does not leak infrastructure into business logic

✓ Keeps responsibilities separated

✓ Does not violate existing ADRs

✓ Keeps Guardrails as its own port/adapter — never inlined into a router, repository, or provider

✓ Places Guardrails before Validators in every workflow that produces AI content (never after, never in parallel as an optional check)

---

# Code Quality

The code:

✓ Is readable

✓ Uses meaningful names

✓ Has no duplication

✓ Has small focused functions

✓ Has single responsibility classes

✓ Has no magic numbers

✓ Has no hardcoded configuration

✓ Uses constants where appropriate

✓ Represents guardrail outcomes with a typed `GuardrailResult`, never a raw dict or boolean

---

# Python Standards

✓ Python 3.13 compatible

✓ Ruff compliant

✓ Black formatted

✓ Import order correct

✓ Strict typing

✓ Public functions typed

✓ Public classes documented

✓ Google style docstrings

---

# Error Handling

✓ Uses typed exceptions

✓ Handles expected failures

✓ Does not swallow exceptions

✓ Returns standardized API errors

✓ Includes useful error messages

✓ Raises a typed `GuardrailRejectionError` (with violation codes) on rejection — never a generic exception, never a silent fallback to "approved"

✓ Never catches a guardrail rejection and proceeds with the unapproved content

---

# Logging

✓ No print()

✓ Structured logging

✓ Important operations logged

✓ Failures logged

✓ Sensitive data excluded

✓ Request IDs included

✓ Every guardrail execution logs its profile, status (approved/repaired/rejected), violation codes, and repair actions

✓ Full resume content and job description text are never logged at INFO level or above

---

# Database

If database changes exist:

✓ Models updated

✓ Alembic migration generated

✓ Migration reviewed

✓ Repository updated

✓ Transaction boundaries verified

✓ Queries optimized

✓ Repository methods that persist AI-generated content reject or refuse (structurally, where possible) any input whose `GuardrailResult.status` is not `approved` or `repaired`

✓ `guardrail_events` records are written for every guardrail execution relevant to the change

---

# API

If API changes exist:

✓ Request schema created

✓ Response schema created

✓ Validation implemented

✓ Status codes correct

✓ OpenAPI updated

✓ Error responses documented

✓ Guardrail rejection responses are structured and explainable (violation codes, affected section) — never a raw 500 or stack trace

---

# AI Features

If AI changes exist:

✓ Prompt template created

✓ Prompt versioned

✓ Prompt references a guardrail profile in its metadata

✓ Structured output validated

✓ Retry strategy implemented

✓ Timeout configured

✓ Hallucination risk considered

✓ Failure handling implemented

✓ Every LLM response is routed through the Guardrails Engine before any other component consumes it

✓ Correct guardrail profile selected for the task (`rewrite_strict` / `analysis_standard` / `validation_paranoid`)

✓ Guardrails-approved, Guardrails-repaired, and Guardrails-rejected code paths are all implemented and tested — not just the happy path

✓ Repair actions (if any) are logged and surfaced to the caller, not applied silently and invisibly

---

# RAG Features

If RAG changes exist:

✓ Chunking verified

✓ Embeddings validated

✓ Retrieval tested

✓ Context size checked

✓ Sources preserved

✓ Duplicate chunks removed

✓ Retrieved context is scanned by the Guardrails prompt-injection detector before being interpolated into a prompt

---

# Guardrails

If the change touches guardrail validators, profiles, or any AI-output-consuming code path:

✓ The correct guardrail profile is applied for the call site

✓ Guardrails runs immediately after the provider call, before any business logic touches the output

✓ All three outcomes (`approved`, `repaired`, `rejected`) are explicitly handled — none falls through to a default

✓ A rejection produces a typed `GuardrailRejectionError` with violation codes, surfaced to the caller (API error, workflow `Failed` state, or equivalent) — never swallowed

✓ Repairs are logged and included in the audit trail (`guardrail_events`)

✓ New or modified validators have a positive test, a targeted negative test, and at least one adversarial test (known prompt-injection pattern or known hallucination case)

✓ Validator changes do not regress the guardrail evaluation suite (see Evaluation-Driven Development / ADR-0010)

✓ No validator combines an AI-safety check with a business-rule check — each validator does exactly one thing

✓ Guardrails Engine is not mocked in tests meant to verify end-to-end AI-safety behavior

---

# Security

✓ Inputs validated
✓ Uploaded files validated
✓ Secrets protected
✓ No credentials logged
✓ No SQL injection risks
✓ No prompt injection risks
✓ No unsafe deserialization
✓ PII/secret scanning of AI output is delegated to the Guardrails PII/Secret Scanner, not reimplemented ad hoc
✓ Unsafe LaTeX commands in AI-generated text are blocked by the Guardrails LaTeX Safety Validator before reaching the rendering engine

---

# Performance

✓ No unnecessary queries

✓ Async APIs used

✓ Connections reused

✓ Expensive work cached

✓ Pagination implemented

✓ Large payloads streamed when appropriate

✓ Independent guardrail validators run concurrently where they have no data dependency on each other

---

# Testing

Minimum:

✓ Unit tests

✓ Integration tests

✓ Failure tests

✓ Edge cases

✓ Regression tests

✓ Guardrail-specific tests where AI output is involved (positive, negative, adversarial — see Guardrails section above)

Tests must pass.

---

# Static Analysis

The following commands succeed:

ruff check .

ruff format .

mypy .

pytest

No warnings ignored.

---

# Documentation

✓ Public APIs documented

✓ Architecture updated if required

✓ ADR created if architectural change

✓ README updated if necessary

✓ Engineering docs updated

✓ Guardrail profile changes or new validators documented in the Guardrails Architecture reference

---

# Deployment

If deployment changes exist:

✓ Docker updated

✓ Environment variables documented

✓ Health checks verified

✓ Startup validated

✓ Backward compatibility checked

✓ Guardrail configuration (enabled validators, profiles, thresholds) is environment-driven, not hardcoded per deployment

---

# Final Verification

Before completion ask:

Can another engineer understand this?

Can another engineer test this?

Can another engineer deploy this?

Can another engineer maintain this?

If this change produces or consumes AI output, can I point to the exact line where it is passed through the Guardrails Engine?

If this change produces or consumes AI output, have I verified what happens on `rejected` — not just on `approved`?

If any answer is NO,

the implementation is NOT DONE.

---

# Completion Checklist

Only mark a task complete when ALL checks pass.

A feature that works only when the LLM behaves well is not done — it must also
be proven correct when the LLM hallucinates, returns malformed output, or is
targeted by a prompt injection attempt.

Never assume.

Always verify.

# Code Review Checklist

> Project: Tailr
> Version: 1.0

---

# Purpose

This checklist is executed after every implementation.

The objective is to review code like a senior software engineer before merging.

Never skip this review.

If the change produces or consumes AI-generated content, this review is also
an AI-safety review. A change that is architecturally clean but bypasses
Guardrails is not reviewable as "approved with suggestions" — it is a
blocking issue.

---

# Step 1 — Understand the Change

Review:

- What changed?
- Why did it change?
- Is the change necessary?
- Does it solve the requested problem?
- Does it produce, transform, or persist AI-generated content? (If yes, Step 10a applies.)

---

# Step 2 — Architecture

Verify:

□ Hexagonal Architecture preserved

□ Domain Driven Design preserved

□ No architecture violations

□ Correct dependency direction

□ Responsibilities remain separated

□ Guardrails Engine invoked as a port/adapter, not inlined into a router, repository, or provider

□ Guardrails runs before Validators, never after or in parallel as an optional step

---

# Step 3 — Readability

Review:

□ Variable names meaningful

□ Function names meaningful

□ Classes clearly named

□ Modules easy to understand

□ Minimal nesting

□ Early returns used

□ No unnecessary abstraction

---

# Step 4 — Complexity

Review:

□ Functions under 60 lines

□ Classes under 300 lines

□ Cyclomatic complexity acceptable

□ No duplicated logic

□ No dead code

□ Each guardrail validator checks exactly one thing (no validator mixing safety and business logic)

---

# Step 5 — Typing

Verify:

□ Public functions typed

□ Return types defined

□ Pydantic models typed

□ No Any unless justified

□ Guardrail outcomes typed as `GuardrailResult`, never a raw dict or bare boolean

---

# Step 6 — Error Handling

Review:

□ Exceptions typed

□ Errors handled gracefully

□ Messages useful

□ No generic Exception

□ No RuntimeError

□ `GuardrailRejectionError` raised on rejection, carrying violation codes

□ No `except` block that catches a guardrail rejection and continues as if it were approved

---

# Step 7 — Logging

Review:

□ Important operations logged

□ Errors logged

□ Sensitive data excluded

□ Request ID propagated

□ No print()

□ Guardrail runs log profile, status, violation codes, and repair actions

□ Full resume/JD content not logged at INFO level or above

---

# Step 8 — Database

If applicable:

□ Repository pattern respected

□ Queries optimized

□ Transactions correct

□ Async APIs used

□ Migration generated

□ Repository refuses (or is structurally incapable of accepting) AI-generated content that is not `approved`/`repaired`

□ `guardrail_events` written for auditability where relevant

---

# Step 9 — API

Review:

□ Validation complete

□ Response models correct

□ Status codes correct

□ Versioning respected

□ Error responses standardized

□ Guardrail rejections surfaced as structured, explainable API errors — never a raw 500 or stack trace

---

# Step 10 — AI

Review:

□ Prompt externalized

□ Prompt references a guardrail profile

□ Structured output validated

□ Timeout handled

□ Retry configured

□ Provider abstraction used

□ Raw provider output passed through Guardrails before any other component touches it

---

# Step 10a — Guardrails

Applies whenever the change touches AI-generated content, a validator, or a guardrail profile.

Review:

□ Correct profile applied for the call site (`rewrite_strict` / `analysis_standard` / `validation_paranoid`)

□ Guardrails invoked immediately after the provider call, before business logic

□ All three outcomes handled explicitly — `approved`, `repaired`, `rejected` — none falls through to an implicit default

□ Rejections are surfaced as typed errors, not swallowed, logged-only, or downgraded to a warning

□ Repairs are logged and included in the audit trail, not applied silently

□ New/modified validators single-purpose (schema, JSON, injection, hallucination, integrity, PII, ATS, LaTeX safety — never combined)

□ Positive test, targeted negative test, and at least one adversarial test present

□ Guardrail evaluation suite re-run and not regressed (see ADR-0010, Evaluation-Driven Development)

□ Guardrails Engine not mocked in tests intended to verify end-to-end AI-safety behavior

---

# Step 11 — RAG

Review:

□ Chunking correct

□ Retrieval efficient

□ Context bounded

□ Duplicate chunks removed

□ Sources preserved

□ Retrieved context scanned by the Guardrails prompt-injection detector before being interpolated into a prompt

---

# Step 12 — Security

Review:

□ Input validation

□ Output sanitization

□ Authentication respected

□ Authorization respected

□ Secrets protected

□ Prompt injection considered

□ PII/secret scanning of AI output delegated to the Guardrails PII/Secret Scanner, not reimplemented ad hoc

□ Unsafe LaTeX commands in AI-generated text blocked by the Guardrails LaTeX Safety Validator before rendering

---

# Step 13 — Performance

Review:

□ Async throughout

□ No blocking calls

□ Clients reused

□ Database efficient

□ Memory reasonable

□ Caching opportunities identified

□ Independent guardrail validators run concurrently where there is no data dependency between them

---

# Step 14 — Testing

Review:

□ Unit tests added

□ Integration tests added

□ Edge cases covered

□ Failures covered

□ Tests readable

□ Guardrail approved / repaired / rejected paths all covered, not just the happy path

---

# Step 15 — Documentation

Review:

□ Docstrings updated

□ README updated

□ ADR updated (if required)

□ Engineering docs updated

□ Guardrails Architecture reference updated if a validator or profile changed

---

# Step 16 — Production Readiness

Ask:

Can this run in production today?

Would I deploy this?

Would another engineer understand it?

Would I maintain this in six months?

If this change touches AI-generated content, can I point to the exact line where Guardrails is invoked, and have I seen a test proving the `rejected` path works?

If any answer is NO,

the change requires another review.

---

# Review Verdict

Use exactly one outcome:

## APPROVED

All quality gates passed.

---

## APPROVED WITH SUGGESTIONS

No blocking issues.

Minor improvements recommended.

---

## CHANGES REQUESTED

Architecture, correctness, testing, security,
maintainability, or Guardrails issues found.

A missing, bypassed, or improperly-scoped Guardrails check is always a
blocking issue. It can never be filed as a "suggestion" — it must be
CHANGES REQUESTED.

Must be fixed before merge.

---

# Final Principle

Review code as if you will maintain it for the next five years.

Prefer long-term quality over short-term convenience.

AI-generated content that reaches a user without passing through Guardrails
is not a quality issue to note for later — it is a trust and safety failure.
Treat it accordingly.

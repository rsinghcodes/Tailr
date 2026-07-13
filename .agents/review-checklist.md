# Code Review Checklist

> Project: Tailr
> Version: 1.0

---

# Purpose

This checklist is executed after every implementation.

The objective is to review code like a senior software engineer before merging.

Never skip this review.

---

# Step 1 — Understand the Change

Review:

- What changed?
- Why did it change?
- Is the change necessary?
- Does it solve the requested problem?

---

# Step 2 — Architecture

Verify:

□ Hexagonal Architecture preserved

□ Domain Driven Design preserved

□ No architecture violations

□ Correct dependency direction

□ Responsibilities remain separated

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

---

# Step 5 — Typing

Verify:

□ Public functions typed

□ Return types defined

□ Pydantic models typed

□ No Any unless justified

---

# Step 6 — Error Handling

Review:

□ Exceptions typed

□ Errors handled gracefully

□ Messages useful

□ No generic Exception

□ No RuntimeError

---

# Step 7 — Logging

Review:

□ Important operations logged

□ Errors logged

□ Sensitive data excluded

□ Request ID propagated

□ No print()

---

# Step 8 — Database

If applicable:

□ Repository pattern respected

□ Queries optimized

□ Transactions correct

□ Async APIs used

□ Migration generated

---

# Step 9 — API

Review:

□ Validation complete

□ Response models correct

□ Status codes correct

□ Versioning respected

□ Error responses standardized

---

# Step 10 — AI

Review:

□ Prompt externalized

□ Structured output validated

□ Timeout handled

□ Retry configured

□ Provider abstraction used

---

# Step 11 — RAG

Review:

□ Chunking correct

□ Retrieval efficient

□ Context bounded

□ Duplicate chunks removed

□ Sources preserved

---

# Step 12 — Security

Review:

□ Input validation

□ Output sanitization

□ Authentication respected

□ Authorization respected

□ Secrets protected

□ Prompt injection considered

---

# Step 13 — Performance

Review:

□ Async throughout

□ No blocking calls

□ Clients reused

□ Database efficient

□ Memory reasonable

□ Caching opportunities identified

---

# Step 14 — Testing

Review:

□ Unit tests added

□ Integration tests added

□ Edge cases covered

□ Failures covered

□ Tests readable

---

# Step 15 — Documentation

Review:

□ Docstrings updated

□ README updated

□ ADR updated (if required)

□ Engineering docs updated

---

# Step 16 — Production Readiness

Ask:

Can this run in production today?

Would I deploy this?

Would another engineer understand it?

Would I maintain this in six months?

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
or maintainability issues found.

Must be fixed before merge.

---

# Final Principle

Review code as if you will maintain it for the next five years.

Prefer long-term quality over short-term convenience.

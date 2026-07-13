# AI Engineering Workflow

> Project: Tailr
> Version: 1.0
> Status: Production

---

# Purpose

This document defines the mandatory workflow every AI coding agent must follow.

The workflow exists to ensure:

- Architectural consistency
- Production quality
- Minimal technical debt
- Predictable implementations
- Safe refactoring

No code should be written without following this workflow.

---

# Core Philosophy

Never code first.

Understand first.

Design second.

Implement third.

Verify fourth.

Review fifth.

Document last.

---

# Global Workflow

Every implementation must follow this sequence.

```

Understand Requirement

↓

Read AGENTS.md

↓

Read Architecture Documents

↓

Read Relevant ADRs

↓

Identify Affected Modules

↓

Create Implementation Plan

↓

Identify Risks

↓

Implement Incrementally

↓

Run Static Analysis

↓

Run Tests

↓

Perform Architecture Review

↓

Update Documentation

↓

Produce Summary

```

Never skip a step.

---

# STEP 1 — Understand the Request

Before writing code, determine:

- What problem is being solved?
- What feature is affected?
- Which business capability changes?
- Is the request complete?
- Are there hidden assumptions?
- Is the request compatible with architecture?

If requirements are ambiguous:

STOP

Request clarification.

Never guess.

---

# STEP 2 — Read Context

Always read:

AGENTS.md

Then read:

Relevant files inside:

.agents/

Knowledge

Rules

Architecture

ADRs

Do not rely on memory.

Repository documentation always wins.

---

# STEP 3 — Determine Impact

Identify:

Files to modify

Files to create

Public APIs affected

Database changes

Configuration changes

Migration requirements

Testing requirements

Documentation changes

---

# STEP 4 — Architecture Validation

Before coding verify:

Does this violate DDD?

Does this violate Hexagonal Architecture?

Does this introduce circular dependencies?

Does this expose infrastructure?

Does this leak business logic?

If yes:

Stop.

Redesign.

---

# STEP 5 — Create an Implementation Plan

Before coding produce an internal plan.

The plan should include:

Modules

Interfaces

Classes

Functions

Dependencies

Testing strategy

Migration strategy

Rollback strategy

Implementation should never begin without a design.

---

# STEP 6 — Incremental Development

Never generate massive files.

Implement one logical unit at a time.

Recommended order:

Interfaces

↓

Domain

↓

Infrastructure

↓

Application

↓

API

↓

Tests

↓

Documentation

---

# STEP 7 — Coding Rules

While coding:

Prefer pure functions.

Prefer composition.

Avoid global state.

Avoid side effects.

Keep functions focused.

Avoid duplication.

Do not prematurely optimize.

---

# STEP 8 — Logging

Every important operation must log:

Start

Completion

Failure

Duration

Request ID

Never log:

Passwords

Tokens

Secrets

PII

---

# STEP 9 — Error Handling

Every failure must:

Raise typed exceptions.

Return standardized responses.

Include enough diagnostic information.

Never expose stack traces to API users.

---

# STEP 10 — Validation

Validate:

Input

Output

Environment

Configuration

External providers

Uploaded files

LLM responses

---

# STEP 11 — Testing

Every feature requires:

Unit tests

Integration tests

Failure tests

Edge case tests

Regression tests

Coverage should increase over time.

---

# STEP 12 — Static Analysis

Before completion run:

Ruff

↓

Black

↓

MyPy

↓

Pytest

No code should be considered complete otherwise.

---

# STEP 13 — Documentation

Update documentation whenever:

Architecture changes

Database changes

API changes

Configuration changes

Deployment changes

Agent behavior changes

Workflow changes

---

# STEP 14 — Code Review

Review code for:

Readability

Maintainability

Performance

Security

Scalability

Architecture

Naming

Error handling

Logging

Testing

---

# STEP 15 — Production Checklist

Before considering a feature complete:

✓ No TODO comments

✓ No print()

✓ No debug code

✓ No unused imports

✓ No dead code

✓ No duplicated logic

✓ No architecture violations

✓ Proper typing

✓ Proper logging

✓ Tests passing

✓ Documentation updated

---

# Refactoring Rules

Refactor only when:

Complexity decreases.

Readability improves.

Architecture improves.

Performance improves.

Test coverage remains.

Never refactor for personal preference.

---

# Database Changes

When changing database:

Update models

Generate migration

Review migration

Test migration

Update repositories

Update documentation

Never manually edit production migrations unless necessary.

---

# API Changes

Every API change requires:

Request model

Response model

Validation

Documentation

Tests

Version compatibility

---

# AI Features

Before implementing AI:

Verify provider abstraction.

Verify prompt templates.

Verify structured output.

Validate responses.

Add retries.

Handle rate limits.

Handle provider failures.

Never trust model output.

---

# RAG Features

Always implement:

Chunking

Embeddings

Retrieval

Reranking

Context limits

Citation support

Source attribution

---

# Security Review

Every implementation must verify:

Input validation

Authorization

Authentication

Injection attacks

Prompt injection

SQL injection

XSS

CSRF (if applicable)

Secrets management

---

# Performance Review

Review:

Database queries

Embedding generation

Prompt size

Memory usage

Network requests

Concurrency

Caching opportunities

---

# Final Deliverable

Every completed task should include:

What changed

Why it changed

Architecture impact

Testing performed

Future considerations

Known limitations

```

---

# AI Decision Matrix

When multiple approaches exist:

1. Prefer architecture consistency.

2. Prefer maintainability.

3. Prefer readability.

4. Prefer correctness.

5. Prefer performance.

6. Prefer simplicity.

Never choose a shortcut that creates technical debt.

---

# Failure Policy

If implementation cannot satisfy:

Architecture

Security

Requirements

Performance

Testing

Stop.

Explain why.

Do not fabricate a solution.

---

# Success Criteria

A successful implementation is:

Correct

Tested

Typed

Documented

Maintainable

Observable

Deployable

Production Ready
```

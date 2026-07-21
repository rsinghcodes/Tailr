---
description: AI Engineering Workflow
---

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
- AI output safety

No code should be written without following this workflow.

No AI-generated content should ever reach a user, a repository, or the rendering pipeline without passing through the Guardrails Engine.

---

# Core Philosophy

Never code first.

Understand first.

Design second.

Implement third.

Verify fourth.

Review fifth.

Document last.

If the work touches AI-generated content: never trust it first. Guardrail it first.

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

Read Guardrails Architecture

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

Run Guardrail Evaluation (if AI-related)

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
- Does this request produce, transform, or persist AI-generated content? If yes, Guardrails involvement is mandatory, not optional, for the rest of this workflow.

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

Guardrails Architecture

ADRs

If the change touches an AI agent, a prompt, a retriever, or anything that produces content later consumed by a user, the Guardrails Architecture document and the relevant Guardrail Profile definitions must be read before implementation planning begins.

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

Guardrail validators or profiles affected

Whether a new AI-output-consuming code path is being introduced, and where in that path the Guardrails Engine will be invoked

---

# STEP 4 — Architecture Validation

Before coding verify:

Does this violate DDD?

Does this violate Hexagonal Architecture?

Does this introduce circular dependencies?

Does this expose infrastructure?

Does this leak business logic?

Does this introduce a path where AI-generated content could reach persistence, validation, or rendering without first passing through the Guardrails Engine?

Does this call Guardrails with the correct profile for the task (`rewrite_strict` / `analysis_standard` / `validation_paranoid`)?

If yes to any violation, or no to the Guardrails questions:

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

For AI-related work: which guardrail profile applies, which validators are relevant, and how the `approved` / `repaired` / `rejected` outcomes are each handled downstream

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

Guardrails Integration (for any AI-output-consuming path)

↓

Application

↓

API

↓

Tests

↓

Documentation

Guardrails integration is not an afterthought bolted on at the end — it is implemented alongside the Infrastructure layer that produces the AI output it protects, before Application code is written to consume that output.

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

Never write a bespoke validation shortcut "just for this feature" instead of using the Guardrails Engine — extend the Guardrails Engine with a new validator if existing coverage is insufficient.

---

# STEP 8 — Logging

Every important operation must log:

Start

Completion

Failure

Duration

Request ID

For guardrail executions, also log:

Guardrail profile used

Status (approved / repaired / rejected)

Violation codes

Repair actions taken

Never log:

Passwords

Tokens

Secrets

PII

Full resume or job description content

---

# STEP 9 — Error Handling

Every failure must:

Raise typed exceptions.

Return standardized responses.

Include enough diagnostic information.

Never expose stack traces to API users.

A Guardrails rejection must raise a typed `GuardrailRejectionError` carrying violation codes and the affected section. It is translated into a structured, explainable error at the API or workflow boundary — never caught and discarded, and never allowed to fall through as a default "approved."

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

LLM responses are validated in two distinct, sequential stages:

1. **Guardrails** — is this output safe, structurally valid, non-hallucinated, free of injected instructions, free of PII/secrets, ATS-compatible, and safe to render?
2. **Business Validators** — is this output correct according to business rules?

Stage 1 always runs before stage 2. Skipping stage 1 "because stage 2 will catch it" is not acceptable — the two stages check different things.

---

# STEP 11 — Testing

Every feature requires:

Unit tests

Integration tests

Failure tests

Edge case tests

Regression tests

Every AI-output-consuming feature additionally requires:

Guardrail approved-path test

Guardrail repaired-path test

Guardrail rejected-path test

At least one adversarial test (known prompt-injection pattern, known hallucination scenario, or similarly documented attack)

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

If the change touches guardrail validators, prompts, or AI-output-consuming code, also run the guardrail evaluation/adversarial suite.

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

Guardrail validators, profiles, or thresholds change

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

Guardrails coverage and correctness (see Code Review Checklist, Step 10a)

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

✓ No AI-output-consuming path that skips the Guardrails Engine

✓ `approved`, `repaired`, and `rejected` outcomes all explicitly handled

---

# Refactoring Rules

Refactor only when:

Complexity decreases.

Readability improves.

Architecture improves.

Performance improves.

Test coverage remains.

Never refactor for personal preference.

Refactoring a guardrail validator additionally requires re-running its adversarial test suite and confirming detection rates have not regressed before the refactor is considered complete.

---

# Database Changes

When changing database:

Update models

Generate migration

Review migration

Test migration

Update repositories

Update documentation

Ensure repositories persisting AI-generated content still reject ungated (non-`approved`/`repaired`) input after the schema change

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

Guardrail rejection error shape documented, if the endpoint can produce one

---

# AI Features

Before implementing AI:

Verify provider abstraction.

Verify prompt templates.

Verify prompt references a guardrail profile.

Verify structured output.

Validate responses through the Guardrails Engine before any other consumer sees them.

Add retries.

Handle rate limits.

Handle provider failures.

Never trust model output — "never trust" means invoking Guardrails, not merely writing a comment saying output should be checked.

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

Prompt-injection scanning of retrieved context before it is interpolated into a prompt

---

# Security Review

Every implementation must verify:

Input validation

Authorization

Authentication

Injection attacks

Prompt injection — delegated to the Guardrails Prompt Injection Detector, not reimplemented per feature

SQL injection

XSS

CSRF (if applicable)

Secrets management

PII leakage in AI output — delegated to the Guardrails PII/Secret Scanner

Unsafe LaTeX in AI output — delegated to the Guardrails LaTeX Safety Validator

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

Guardrail validator concurrency (independent validators should run in parallel, not sequentially, where there is no data dependency)

---

# Final Deliverable

Every completed task should include:

What changed

Why it changed

Architecture impact

Testing performed

Guardrails impact (new/modified validators, profiles, or coverage) if applicable

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

A design that is simpler or faster but removes, weakens, or bypasses a Guardrails check is not an acceptable trade-off under any ranking above. Guardrails coverage is a hard constraint, not a factor to be traded off against.

Never choose a shortcut that creates technical debt.

---

# Failure Policy

If implementation cannot satisfy:

Architecture

Security

Requirements

Performance

Testing

Guardrails coverage for AI-generated content

Stop.

Explain why.

Do not fabricate a solution.

Do not ship an AI feature with a "temporarily disabled" or "TODO: add guardrails later" guardrail check. If Guardrails coverage cannot be completed, the feature is not done — stop and explain why, per this policy.

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

Guardrail-Compliant — every AI-generated content path is protected, every outcome is handled, and every rejection is explainable
```

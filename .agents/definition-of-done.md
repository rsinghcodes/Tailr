# Definition of Done (DoD)

> Project: Tailr
> Version: 1.0

---

# Purpose

This document defines the minimum quality requirements before any task,
feature, bug fix, refactor, or architectural change can be considered complete.

If every requirement is not satisfied, the task is NOT DONE.

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

---

# Logging

✓ No print()

✓ Structured logging

✓ Important operations logged

✓ Failures logged

✓ Sensitive data excluded

✓ Request IDs included

---

# Database

If database changes exist:

✓ Models updated

✓ Alembic migration generated

✓ Migration reviewed

✓ Repository updated

✓ Transaction boundaries verified

✓ Queries optimized

---

# API

If API changes exist:

✓ Request schema created

✓ Response schema created

✓ Validation implemented

✓ Status codes correct

✓ OpenAPI updated

✓ Error responses documented

---

# AI Features

If AI changes exist:

✓ Prompt template created

✓ Prompt versioned

✓ Structured output validated

✓ Retry strategy implemented

✓ Timeout configured

✓ Hallucination risk considered

✓ Failure handling implemented

---

# RAG Features

If RAG changes exist:

✓ Chunking verified

✓ Embeddings validated

✓ Retrieval tested

✓ Context size checked

✓ Sources preserved

✓ Duplicate chunks removed

---

# Security

✓ Inputs validated

✓ Uploaded files validated

✓ Secrets protected

✓ No credentials logged

✓ No SQL injection risks

✓ No prompt injection risks

✓ No unsafe deserialization

---

# Performance

✓ No unnecessary queries

✓ Async APIs used

✓ Connections reused

✓ Expensive work cached

✓ Pagination implemented

✓ Large payloads streamed when appropriate

---

# Testing

Minimum:

✓ Unit tests

✓ Integration tests

✓ Failure tests

✓ Edge cases

✓ Regression tests

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

---

# Deployment

If deployment changes exist:

✓ Docker updated

✓ Environment variables documented

✓ Health checks verified

✓ Startup validated

✓ Backward compatibility checked

---

# Final Verification

Before completion ask:

Can another engineer understand this?

Can another engineer test this?

Can another engineer deploy this?

Can another engineer maintain this?

If any answer is NO,

the implementation is NOT DONE.

---

# Completion Checklist

Only mark a task complete when ALL checks pass.

Never assume.

Always verify.

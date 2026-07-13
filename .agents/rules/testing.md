# Testing Rules

Priority: HIGH

---

Every feature requires tests.

No exceptions.

---

# Test Pyramid

Unit Tests

↓

Integration Tests

↓

End-to-End Tests

---

# Unit Tests

Test

Business Rules

Services

Validators

Utilities

Agents

Never mock business logic.

---

# Integration Tests

Test

Database

Repositories

API

Providers

Use test containers when appropriate.

---

# API Tests

Every endpoint must test

Success

Validation failure

Authentication

Authorization

404

500

---

# AI Tests

Test

Prompt generation

Structured output

Retry logic

Provider failure

Malformed responses

Timeouts

---

# RAG Tests

Chunking

Embeddings

Retrieval

Ranking

Context building

---

# Coverage

Minimum

85%

Critical modules

95%+

---

# Fixtures

Shared fixtures only.

Avoid duplicated setup.

---

# Naming

test_create_resume()

test_invalid_pdf()

test_retry_when_provider_fails()

---

# Mocking

Mock

External APIs

LLMs

Redis

Vector DB

Never mock domain logic.

---

# CI

Tests must pass before merge.

Fail fast.

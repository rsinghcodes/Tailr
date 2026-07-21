# AGENTS.md

> Master Engineering Guide for AI Coding Agents
>
> Project: Tailr
> Version: 1.0
> Status: Production
> Last Updated: 2026-07-12

---

# Purpose

This repository contains the source code for **Tailr**, an AI-powered resume tailoring platform.

This file defines how AI coding agents must behave while working on this repository.

Every AI assistant MUST read this file before making changes.

This file has higher priority than generic coding knowledge.

---

# Mission

Build production-quality software.

Do not build tutorial code.

Do not generate placeholder implementations.

Do not sacrifice architecture for simplicity.

Every change should be deployable.

---

# Product Vision

Tailr enables job seekers to create ATS-optimized resumes by combining:

- Resume Parsing
- Job Description Analysis
- Retrieval-Augmented Generation (RAG)
- Multi-Agent AI
- ATS Validation
- Resume Rewriting
- Resume Scoring

---

# High-Level Architecture

Tailr follows:

- Domain Driven Design (DDD)
- Hexagonal Architecture
- Clean Architecture principles
- Ports & Adapters
- SOLID
- Twelve-Factor App

Dependencies always point inward.

Infrastructure never contains business logic.

---

# Tech Stack

## Backend

Python 3.13

FastAPI

SQLAlchemy 2.x Async

Alembic

PostgreSQL

Redis

Qdrant

LlamaIndex

LangGraph

Ollama

Pydantic v2

HTTPX

OpenTelemetry

Prometheus

## Frontend

Next.js

React

TypeScript

Tailwind CSS

TanStack Query

Zustand

ShadCN UI

React Hook Form

Zod

---

# Primary Design Principles

1. Simplicity over cleverness.

2. Explicit over implicit.

3. Composition over inheritance.

4. Async first.

5. Business logic belongs only inside the Domain/Application layers.

6. Infrastructure is replaceable.

7. Every external dependency must be abstracted.

8. Every module must be independently testable.

9. Every public API must be typed.

10. Never introduce technical debt intentionally.

---

# Project Structure

backend/
|-- agents/
|-- alembic/
|-- app/
|-- api/
|-- application/
|-- config/
|-- core/
|-- domain/
|-- embeddings/
|-- evaluation/
|-- guardrails/
|-- telemetry/
|-- shared/
|-- infrastructure/
|-- workflows/
|-- prompts/
|-- jobs/
|-- parsers/
|-- validators/
|-- workflows/
|-- storage/
|-- rag/
|-- providers/
|-- scratch/
|-- repositories/
|-- services/

frontend/

worker/

docs/

.agents/

---

# Layer Responsibilities

## app/

FastAPI bootstrap only.

Contains:

- middleware
- startup
- shutdown
- lifespan
- app factory

No business logic.

---

## api/

Responsible only for HTTP.

Allowed:

- request validation

- response serialization

- dependency injection

Forbidden:

- SQL

- AI

- repositories

- prompt generation

- business rules

---

## application/

Coordinates business use cases.

Can call:

- repositories

- providers

- domain services

Cannot access FastAPI directly.

---

## domain/

Contains:

- entities

- value objects

- domain services

- business rules

Must not import infrastructure.

---

## infrastructure/

Contains:

- PostgreSQL

- Redis

- Qdrant

- Ollama

- LlamaIndex

- LangGraph

- HTTP clients

Everything here is replaceable.

---

## shared/

Reusable components.

Examples:

Exceptions

Enums

Schemas

Utilities

Response models

Types

Pagination

---

## telemetry/

Logging

Metrics

Tracing

Request IDs

Correlation IDs

OpenTelemetry

No business logic.

---

# Dependency Rule

Allowed

API

↓

Application

↓

Domain

↓

Interfaces

↓

Infrastructure

Forbidden

Infrastructure

↓

Application

Domain

↓

FastAPI

Application

↓

SQLAlchemy Models

Repositories

↓

Routers

---

# AI Provider Rules

Never call an LLM directly.

Always use a Provider abstraction.

Example

Application

↓

LLMProvider Interface

↓

OllamaProvider

OpenAIProvider

HFProvider

---

# Vector Database Rules

Never import Qdrant directly.

Always use:

VectorStore interface

Implementations:

Qdrant

FAISS

Chroma

---

# Repository Rules

Repositories only perform persistence.

Repositories never:

Generate prompts

Call LLMs

Contain business logic

Repositories should be replaceable.

---

# Prompt Rules

Prompt templates belong only in:

prompts/

Never inline prompts inside Python code.

Prompt versions must be tracked.

---

# Agent Rules

Every AI Agent:

Has a single responsibility.

Produces structured output.

Can be tested independently.

Can fail independently.

Never depends directly on another agent implementation.

Communication happens through interfaces.

---

---

# Guardrails Rules

All AI-generated content must pass the Guardrails Engine before it is persisted, indexed, rendered, or returned to the user.

The Guardrails layer is a mandatory trust boundary.

## Mandatory Validators

Every AI output must be checked by:

- Schema Validator
- JSON Validator
- Hallucination Detector
- Resume Integrity Validator
- Prompt Injection Detector
- PII / Secret Scanner
- ATS Validator
- LaTeX Safety Validator

## Hallucination Policy

Agents must never introduce:

- employers not present in the Canonical Resume Model,
- projects not present in the source resume,
- technologies not present in the source resume,
- fabricated metrics,
- altered employment dates,
- unsupported certifications.

If supporting evidence is missing, the content must be rejected.

## Structured Output Requirement

All agents must return typed JSON or Pydantic models.

Free-form text is not allowed across agent boundaries.

## Repair Policy

Recoverable issues (escaping, malformed JSON, markdown fences) should be repaired automatically.

Non-recoverable issues must cause workflow failure.

## Rendering Safety

AI-generated text must never contain dangerous LaTeX commands such as:

- \\input
- \\include
- \\write18
- \\openout
- \\catcode

All special characters must be escaped before rendering.

## Audit Requirement

Every guardrail decision must be logged with:

- workflow_id
- agent_name
- validator_name
- status
- violation_code
- repair_applied
- execution_time_ms

---

# Workflow Rules

Workflow orchestration belongs only inside:

workflows/

Individual agents never orchestrate other agents.

---

# Error Handling

Never expose raw exceptions.

Always raise typed exceptions.

All exceptions must map to standardized API responses.

Guardrail violations must raise typed exceptions such as:

- SchemaValidationError
- HallucinationDetectedError
- PromptInjectionDetectedError
- LatexSafetyError
- ATSValidationError

Guardrail failures are considered business failures, not infrastructure failures.

---

# Logging Rules

No print().

Use the telemetry package.

All logs must be structured.

Every request must include:

Request ID

Correlation ID

Duration

Module

Operation

---

# Security Rules

Validate every external input.

Never trust uploaded files.

Never trust LLM output.

Escape HTML.

Sanitize filenames.

Validate MIME types.

Protect secrets.

Never log credentials.

Never commit API keys.

Run prompt injection detection on all retrieved context.

Run PII and secret scanning on all AI-generated content.

Reject outputs that fail guardrail validation.

LaTeX rendering must occur in a sandboxed environment.

Validation logs must be immutable and auditable.

---

# Performance Rules

Avoid N+1 queries.

Batch embeddings.

Reuse HTTP clients.

Connection pooling enabled.

Cache frequently used prompts.

Stream LLM output when appropriate.

---

# Testing Rules

Every feature requires:

- Unit tests
- Integration tests
- Edge case tests
- Failure tests
- Regression tests
- Guardrail tests

Guardrail tests must include:

- hallucination detection,
- prompt injection attempts,
- malformed JSON,
- ATS validation failures,
- unsafe LaTeX payloads,
- PII leakage scenarios.

No feature is complete without tests.

---

# Documentation Rules

Every public class requires documentation.

Every exported function requires type hints.

Architecture decisions require an ADR.

Large features require engineering documentation.

---

# Code Quality Rules

Maximum function length:

60 lines

Maximum class length:

300 lines

Cyclomatic complexity:

<10 preferred

Avoid deep nesting.

Prefer early returns.

---

# Code Generation Rules

AI assistants MUST:

- Read AGENTS.md first.
- Read relevant ADRs.
- Read architecture documents.
- Understand the feature.
- Design before coding.
- Generate production-ready code.
- Generate tests.
- Add structured logging.
- Add telemetry hooks.
- Add guardrail validation where AI output is used.
- Explain trade-offs.
- Never invent APIs.
- Never fabricate requirements.
- Never bypass the Guardrails Engine.
- Never persist unvalidated AI output.
- Never remove existing architecture without justification.

---

# Definition of Done

A task is complete only if:

- [ ] Code builds
- [ ] Tests pass
- [ ] Ruff passes
- [ ] MyPy passes
- [ ] Documentation updated
- [ ] Architecture preserved
- [ ] Structured logging added
- [ ] Telemetry added
- [ ] Error handling implemented
- [ ] Dependency injection used
- [ ] Guardrail validation added for AI outputs
- [ ] Hallucination checks implemented where required
- [ ] Prompt injection protection added where required
- [ ] No TODO placeholders remain
- [ ] No unvalidated AI output is persisted or rendered

---

# When Unsure

Do not guess.

Ask for clarification.

Or stop and explain the architectural conflict.

Incorrect production code is worse than incomplete code.

---

# Guardrails Enforcement

Any AI coding agent that generates code which:

- bypasses validation,
- persists raw LLM output,
- renders unescaped LaTeX,
- ignores hallucination checks,
- or skips prompt injection protection

is producing **invalid Tailr code**.

The correct behavior is to:

1. Add or reuse the appropriate validator.
2. Return structured validation errors.
3. Log the violation with telemetry.
4. Fail the workflow safely.
5. Preserve auditability.

When implementing new AI features, agents must consult:

- ADR 11-Validation-Guardrails-Engine.md
- 17-Guardrails-Architecture.md
- ADR 10-Evaluation-Driven-Development.md

before generating code.

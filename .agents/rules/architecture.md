---
trigger: always_on
---

# Purpose

This document defines the official software architecture for Tailr.Every implementation must follow this architecture.

If an implementation conflicts with this document, this document takes precedence.

---

# Guiding Principles

Tailr is designed as a long-term production system.

Architecture decisions prioritize:

- Maintainability
- Scalability
- Testability
- Replaceability
- Separation of Concerns
- Low Coupling
- High Cohesion
- AI Safety

Never optimize for writing less code.

Always optimize for writing better software.

AI output is never trusted by default. Every AI-generated artifact must pass through the Guardrails Engine before it is validated, persisted, or rendered.

---

# Architectural Style

Tailr combines:

- Domain Driven Design (DDD)
- Hexagonal Architecture
- Clean Architecture
- SOLID Principles
- Twelve-Factor App
- Guardrails-First AI Safety

These are complementary, not competing.

---

# High-Level Architecture

                  ┌──────────────────────┐
                  │     Frontend         │
                  └──────────┬───────────┘
                             │
                        REST API
                             │
                  ┌──────────▼───────────┐
                  │      API Layer       │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │  Application Layer   │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │    Domain Layer      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │ Infrastructure Layer │
                  └──────────────────────┘

Dependencies always point downward.

Business rules always point upward.

Any output produced by an AI Provider (see Provider Pattern) is not permitted to cross from the Infrastructure Layer back into the Application or Domain layers directly. It must first pass through the **Guardrails Engine**. See "Guardrails Architecture" below.

                  Infrastructure (LLM Provider)
                             │
                        Raw AI Output
                             │
                  ┌──────────▼───────────┐
                  │   Guardrails Engine   │
                  └──────────┬───────────┘
                             │
                     Approved / Repaired
                             │
                  ┌──────────▼───────────┐
                  │  Application Layer    │
                  └──────────────────────┘

Rejected output never reaches the Application or Domain layers. It terminates as a typed error.

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

---

# Layer Responsibilities

## app/

Responsible only for application startup.

Contains:

FastAPI factory

Middleware registration

Lifespan

Startup

Shutdown

Never contains business logic.

---

## api/

Responsible for HTTP only.

Allowed:

Routing

Validation

Dependency Injection

Authentication

Serialization

Forbidden:

Database access

Prompt creation

Business rules

LLM calls

Repository implementation

Guardrail enforcement (guardrails run inside the application/workflow layer, never in routers)

---

## application/

Coordinates use cases.

Examples:

Tailor Resume

Generate Cover Letter

Analyze Job Description

Create Embeddings

Application layer orchestrates work.

Application layer does not contain infrastructure code.

Every use case that consumes AI-generated output must invoke the Guardrails Engine before passing that output to the domain layer or a repository. This call is not optional and must not be skipped for "trusted" or "internal" call sites.

---

## domain/

Contains business knowledge.

Examples:

Entities

Value Objects

Business Rules

Policies

Domain Services

Domain layer must never import FastAPI.

Domain layer must never import SQLAlchemy.

Domain layer must never import HTTP clients.

Domain layer must never import LLM clients or the Guardrails Engine directly. Domain entities and policies define _what_ is immutable or valid; they do not perform AI safety checks themselves. The Application layer is responsible for invoking Guardrails before domain state is mutated.

---

## infrastructure/

Implements interfaces.

Contains:

Database

Redis

Qdrant

Ollama

LlamaIndex

LangGraph

Storage

HTTP clients

No business rules belong here.

Raw provider responses originating here are considered untrusted input the moment they leave the provider adapter. They must be routed through `guardrails/` before any other layer consumes them.

---

## guardrails/

Responsible for AI output safety and integrity. This is the trust boundary between probabilistic AI generation and deterministic business logic.

Contains:

Schema Validator

JSON Validator

Prompt Injection Detector

Hallucination Detector

Resume Integrity Validator

PII / Secret Scanner

ATS Validator

LaTeX Safety Validator

Repair Engine

Guardrail Profiles (e.g. `rewrite_strict`, `analysis_standard`, `validation_paranoid`)

Allowed:

Reading AI output and the Canonical Resume Model (read-only, for hallucination comparison)

Producing a structured Validation Result (`approved` / `repaired` / `rejected`)

Repairing recoverable formatting issues

Emitting guardrail telemetry and audit events

Forbidden:

Calling repositories directly to persist domain state

Making business decisions (e.g. whether a change is a "good" optimization — that belongs to `application/` and `validators/`)

Rendering or compiling output

Silently discarding a rejection (every rejection must be surfaced as a typed error)

The Guardrails layer is provider-independent. It behaves identically regardless of whether the underlying model is Ollama, OpenAI, Anthropic, or any future provider.

---

## validators/

Responsible for deterministic business-rule and schema validation _after_ Guardrails have approved or repaired an output.

Guardrails answer: "Is this output safe, structurally valid, and non-hallucinated?"

Validators answer: "Is this output correct according to business rules (dates, formatting policy, ATS compliance thresholds, etc.)?"

Validators must never run before Guardrails in a workflow. Guardrails is always the first gate after AI generation.

---

## shared/

Reusable building blocks.

Exceptions

Schemas

Enums

Utilities

Pagination

Response Models

Types

Shared code should have no business meaning.

---

## telemetry/

Logging

Metrics

Tracing

Observability

Monitoring

Guardrail outcomes (approved / repaired / rejected), violation codes, and repair events must be emitted here for every guardrail execution.

Cross-cutting concerns only.

---

# Dependency Direction

Correct

API

↓

Application

↓

Domain

↓

Ports

↓

Infrastructure

Also correct (AI generation path)

Infrastructure (Provider)

↓

Guardrails

↓

Application

↓

Domain

Wrong

Infrastructure

↓

Application

Domain

↓

API

Repositories

↓

Routers

Infrastructure (Provider)

↓

Application _(bypassing Guardrails)_

---

# Ports & Adapters

Every external dependency must be abstracted.

Example

Application

↓

ResumeRepository

↓

PostgresRepository

Never inject SQLAlchemy directly into services.

Guardrails is itself exposed as a port so its implementation can evolve (additional validators, different repair strategies) without changing call sites.

Application

↓

GuardrailsEngine (port)

↓

DefaultGuardrailsEngine (adapter: schema + JSON + injection + hallucination + integrity + PII + ATS + LaTeX safety + repair)

---

# Provider Pattern

Every AI model must be hidden.

Application

↓

LLMProvider

↓

OllamaProvider

↓

OpenAIProvider

↓

HFProvider

Application never knows which provider is used.

No provider is trusted more than another. Every provider's output — local or cloud — passes through the same Guardrails Engine with the same profiles. Guardrails must never special-case a provider as "safe to skip."

---

# Vector Store Pattern

Application

↓

VectorStore

↓

Qdrant

↓

FAISS

↓

Chroma

Never call Qdrant directly from services.

Content retrieved from the vector store (job descriptions, career guides, prior resume versions) is external input and must pass through the Guardrails prompt-injection scan before it is assembled into a prompt.

---

# Repository Pattern

Repositories only perform persistence.

Repositories must never:

Call LLMs

Generate prompts

Perform validation

Contain workflows

Bypass or re-implement guardrail checks

Repositories must only ever persist output that already carries an `approved` or `repaired` Guardrails status. A repository must reject (at the type level, if possible) any attempt to persist unvalidated AI output.

Repositories should be replaceable.

---

# Service Pattern

Application Services coordinate work.

They:

Validate business rules

Call repositories

Call providers

Call the Guardrails Engine after every provider call that returns AI-generated content

Return domain objects

They should never:

Execute SQL

Build HTTP responses

Call FastAPI directly

Pass unguarded AI output to a repository or downstream service

---

# Domain Model

Entities contain behavior.

Bad

Resume

name

skills

experience

Good

Resume

calculate_score()

remove_duplicates()

normalize_skills()

Business logic belongs inside entities or domain services.

Immutable facts (employer, dates, technologies, projects, education) are protected first by Guardrails (hallucination + integrity detection) and second by domain invariants. Guardrails is the first line of defense; domain invariants are the last line of defense. Neither layer should assume the other has already enforced correctness.

---

# AI Agent Architecture

Every AI agent must have exactly one responsibility.

Planner

↓

Resume Analyzer

↓

JD Analyzer

↓

Retriever

↓

Writer

↓

Guardrails Engine

↓

ATS Validator

↓

Critic

↓

Optimizer

↓

Final Validator

Agents communicate through structured interfaces.

Agents never call each other directly.

Agents never call the Guardrails Engine conditionally. Every agent that produces content consumed downstream (Writer, Optimizer, Critic) routes its raw output through Guardrails before that output is visible to the next agent or persisted.

Agents themselves must never implement their own ad-hoc validation logic as a substitute for Guardrails.

---

# LangGraph Workflow

Workflows coordinate agents.

Planner

↓

Retrieve

↓

Generate

↓

Guardrails

↓

Validate

↓

Critique

↓

Rewrite

↓

Guardrails

↓

Score

↓

Complete

Only workflows orchestrate agents.

Guardrails is not a one-time gate at the end of the workflow — it runs after **every** generation or rewrite step, since each step produces new AI output that must be independently checked.

A workflow node may only transition forward if the preceding Guardrails check returned `approved` or `repaired`. A `rejected` result transitions the workflow to a terminal `Failed` state with a structured error; it must never be silently retried into the same step without a policy-defined retry/backoff rule.

---

# RAG Architecture

Document

↓

Parser

↓

Chunker

↓

Embedding Model

↓

Vector Store

↓

Retriever

↓

Reranker

↓

Guardrails (prompt-injection scan on retrieved context)

↓

Prompt Builder

↓

LLM

↓

Guardrails (schema, hallucination, integrity, PII, ATS, LaTeX safety, repair)

↓

Structured Output

Every stage must be replaceable.

Retrieved context is external, untrusted input in the same sense as a file upload or an HTTP request body. It must be scanned for prompt-injection patterns before it is interpolated into a prompt, and the final LLM output must be scanned again before it is treated as structured output.

---

# Guardrails Architecture

Guardrails is the mandatory trust boundary between probabilistic AI generation and deterministic business logic. No AI-generated content may reach persistence, validation, or rendering without passing through this engine.

## Design Principles

**Fail Closed** — if a validator cannot determine safety, the output is rejected, not passed through.

**Defense in Depth** — multiple independent validators run in sequence; no single validator is treated as sufficient on its own.

**Deterministic Validation** — guardrail checks are implemented as deterministic code wherever possible, not delegated to another LLM call. Where an LLM-based check is unavoidable (e.g. a repair pass), its output is still subject to schema validation.

**Repair Before Reject** — recoverable issues (malformed JSON, stray markdown fences, unescaped characters) are repaired automatically rather than failing the whole workflow.

**Full Auditability** — every violation, repair, and rejection is persisted for debugging, evaluation, and compliance.

## Validation Pipeline

Raw LLM Output

↓

JSON Parse

↓

Schema Validation

↓

Prompt Injection Detection

↓

Hallucination Detection (compared against the Canonical Resume Model)

↓

Resume Integrity Validation

↓

PII / Secret Scan

↓

ATS Formatting Validation

↓

LaTeX Safety Validation

↓

Repair (if a recoverable issue was found)

↓

Validation Result: Approved / Repaired / Rejected

## Validation Result Contract

Every guardrail execution returns a structured, typed result:

status: approved | repaired | rejected

repair_applied: boolean

violations: list of structured violation codes

warnings: list of non-blocking warnings

metadata: validator count, execution time

Callers must branch on `status`. A missing or unhandled `status` value is a bug, not a default-approve condition.

## Guardrail Profiles

Different call sites require different strictness. Profiles are configuration, not code branches.

`rewrite_strict` — hallucination detection, integrity validation, ATS validation, LaTeX validation. Used for any content that modifies resume text.

`analysis_standard` — schema validation, JSON validation, prompt injection detection. Used for read-only analysis (JD analysis, resume analysis).

`validation_paranoid` — all validators enabled, zero warnings tolerated. Used immediately before final PDF rendering.

Agents and services select a profile by name; they never hand-assemble a custom validator chain inline.

## Placement in the Architecture

Guardrails sits logically after the Infrastructure Layer's AI Provider adapters and before the Application layer resumes control. It is implemented as its own module (`guardrails/`) and exposed to the rest of the system as a port (`GuardrailsEngine`), consistent with the Ports & Adapters pattern used everywhere else in this architecture. It is not middleware, and it is not implemented inside `api/`.

---

# Configuration

No hardcoded values.

Everything configurable.

Environment variables

Typed settings

Validation at startup

Guardrail profiles, thresholds, and enabled validators are configuration-driven, not hardcoded, so that strictness can be tuned per environment (development / staging / production) without a code change.

---

# Dependency Injection

Never instantiate dependencies manually.

Correct

Service

↓

Repository Interface

↓

Implementation

Service

↓

GuardrailsEngine Interface

↓

Implementation

Wrong

service = ResumeService()

inside a router.

guardrails_result = SomeCustomValidator().check(output)

inline inside a service instead of using the injected GuardrailsEngine port.

---

# Error Handling

Every layer raises typed exceptions.

API converts exceptions into HTTP responses.

Never expose internal stack traces.

A Guardrails rejection must be raised as its own typed exception (e.g. `GuardrailRejectionError`) carrying the violation codes, not swallowed or converted into a generic 500. The API layer maps it to a structured, explainable error response — never a stack trace, and never a silently "successful" response with corrupted content.

---

# Logging

Every important operation logs:

Start

End

Duration

Failure

Request ID

Module

Guardrail executions additionally log: guardrail profile used, validator outcomes, violation codes, repair actions taken, and whether the result was approved, repaired, or rejected.

Never use print().

---

# Testing Strategy

Every layer is independently testable.

Unit Tests

↓

Guardrail Tests

↓

Application

↓

Repository

↓

API

↓

Integration Tests

Mock infrastructure.

Never mock business logic.

Never mock the Guardrails Engine in integration or workflow tests unless the test is explicitly and exclusively about a component upstream of Guardrails. AI safety behavior must be exercised with real (or realistic adversarial) inputs, including known prompt-injection patterns and known hallucination cases, on a regular basis.

---

# Security

Validate all inputs.

Validate uploaded files.

Never trust AI output.

Never trust external APIs.

Escape user content.

Protect secrets.

Never trust AI output is enforced structurally, not just as a guideline: it means every AI output-consuming code path is required to have a Guardrails call in front of it. PII and secret scanning are handled inside the Guardrails Engine, not bolted on separately downstream.

---

# Scalability

System must support:

Horizontal scaling

Multiple AI providers

Multiple vector databases

Background workers

Streaming responses

Distributed tracing

Guardrails running as an independently scalable stage (parallel validators, async execution)

Future microservice extraction

without major refactoring.

---

# Anti-Patterns

Never place SQL inside routers.

Never call Ollama inside API routes.

Never create prompts inside services.

Never use global database sessions.

Never expose SQLAlchemy models outside repositories.

Never couple domain to infrastructure.

Never use synchronous I/O.

Never use print().

Never introduce circular imports.

Never persist, render, or return AI-generated content that has not passed through the Guardrails Engine.

Never treat a Guardrails "approved" result as permanent — a new generation always requires a new Guardrails check, even if a previous version of the same content was already approved.

Never implement one-off validation logic inside an agent or service as a substitute for the Guardrails Engine.

Never allow a guardrail rejection to fail silently or default to "approved."

---

# Architecture Review Checklist

Every Pull Request must answer:

Does this respect DDD?

Does this respect Hexagonal Architecture?

Are dependencies pointing inward?

Is infrastructure replaceable?

Is business logic isolated?

Are interfaces used?

Can this module be tested independently?

Does every new AI-output-consuming code path invoke the Guardrails Engine before that output is persisted, validated, or rendered?

Is the correct Guardrail profile applied for this call site?

Are guardrail rejections surfaced as typed errors with violation codes, rather than swallowed or logged only?

If any answer is NO,

the implementation should be redesigned.

---

# Final Principle

Architecture is more important than implementation.

A feature can always be rewritten.

A bad architecture becomes permanent.

Protect the architecture first.

AI-generated content that bypasses Guardrails is not a shortcut — it is a defect. Protect the trust boundary as strictly as the architecture itself.

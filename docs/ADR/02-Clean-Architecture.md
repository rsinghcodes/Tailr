# ADR-0002: Adopt Clean Architecture with Hexagonal Boundaries for the Backend

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr is not a traditional CRUD application.

The platform consists of multiple independent subsystems:

- Resume Parser
- Knowledge Layer
- RAG Engine
- Multi-Agent Workflow
- Guardrails Engine
- Validation Engine
- ATS Engine
- Rendering Engine
- Version Manager
- Evaluation Pipeline

These components interact with:

- PostgreSQL
- Qdrant
- Redis
- Ollama
- Object Storage
- External LLM providers
- PDF compilation tools
- Observability systems

Without strict architectural boundaries, business logic would become tightly coupled to frameworks and infrastructure, making testing, maintenance, and future evolution difficult.

The system requires an architecture that:

- isolates business rules,
- enforces dependency inversion,
- supports deterministic validation,
- enables unit testing without infrastructure,
- allows infrastructure replacement,
- supports future microservices,
- integrates AI guardrails as a first-class concern.

---

# Decision

Tailr adopts **Clean Architecture** with **Hexagonal (Ports & Adapters) boundaries** and selected **Domain-Driven Design (DDD)** principles.

The backend is organized into independent layers.

```text
Presentation Layer
(FastAPI, REST API, WebSocket)
        │
        ▼
Application Layer
(Use Cases / Services)
        │
        ▼
Ports & Interfaces
(Repository & Provider Contracts)
        │
        ▼
Domain Layer
(Entities, Value Objects, Policies)
        ▲
        │
Infrastructure Adapters
(PostgreSQL, Qdrant, Redis, Ollama, Storage)
```

Dependencies always point **inward**.

The Domain layer must not depend on FastAPI, SQLAlchemy, Qdrant, Redis, Ollama, or any external framework.

---

# Decision Drivers

The architecture must:

- separate business logic from infrastructure,
- simplify testing,
- support AI workflow orchestration,
- allow multiple storage backends,
- support local and cloud LLMs,
- enable future microservices,
- reduce framework lock-in,
- support observability and tracing,
- enforce guardrails consistently.

---

# Layer Responsibilities

## Presentation Layer

Responsible for:

- HTTP APIs
- Authentication
- Authorization
- Request validation
- Response serialization
- Streaming responses

**No business logic exists here.**

---

## Application Layer

Responsible for:

- Workflow orchestration
- Transactions
- Use cases
- Coordination between services
- Retry handling
- State transitions

Examples:

- Optimize Resume
- Analyze Job Description
- Generate ATS Report
- Compile Resume PDF
- Evaluate Prompt Quality

The Application layer depends only on **Ports / Interfaces** and the **Domain layer**.

---

## Domain Layer

Contains:

- Resume entity
- Job Description entity
- Resume Version entity
- Validation policies
- ATS scoring rules
- Resume integrity rules
- Business exceptions
- Domain events

This layer contains the core business knowledge and remains completely framework-independent.

---

## Ports & Interfaces

Defines contracts for external dependencies.

Examples:

```text
ResumeRepository
JobDescriptionRepository
KnowledgeRepository
PromptRepository
LLMProvider
EmbeddingProvider
VectorStore
ObjectStorage
PDFCompiler
```

Infrastructure adapters implement these interfaces.

---

## Infrastructure Adapters

Responsible for:

- PostgreSQL
- Redis
- Qdrant
- Ollama
- OpenAI / Anthropic / Gemini (future)
- File storage
- PDF generation
- External APIs
- Telemetry exporters

Infrastructure can change without affecting business logic.

---

# Knowledge Layer

The Knowledge Layer is implemented inside the infrastructure boundary but exposed through ports.

Responsibilities:

- semantic chunking
- embedding generation
- metadata enrichment
- vector indexing
- hybrid retrieval
- reranking

This separation allows Qdrant to be replaced without changing application logic.

---

# Guardrails Layer

A dedicated Guardrails layer is introduced between AI generation and business validation.

Responsibilities:

- JSON validation
- schema validation
- prompt injection detection
- hallucination detection
- PII detection
- resume integrity checks
- ATS formatting checks
- output repair

The Guardrails layer is provider-independent and reusable across all AI workflows.

---

# Repository Pattern

Application services communicate through interfaces.

Example:

```text
ResumeRepository
KnowledgeRepository
WorkflowRepository
PromptRepository
EvaluationRepository
```

Infrastructure provides concrete implementations.

Repositories are responsible only for persistence and retrieval.

Repositories must **not**:

- call LLMs,
- generate prompts,
- perform business validation,
- orchestrate workflows.

---

# Dependency Rule

## Allowed

```text
Presentation
    ↓
Application
    ↓
Ports
    ↓
Domain
```

```text
Infrastructure ──implements──> Ports
```

---

## Forbidden

```text
Domain → FastAPI
Domain → SQLAlchemy
Domain → Qdrant
Domain → Redis
Domain → Ollama
Domain → HTTP clients
```

```text
Application → SQLAlchemy
Application → Qdrant
Application → Ollama
```

The Domain layer remains completely framework-independent.

---

# Project Structure

```text
backend/
├── app/
├── api/
├── application/
├── domain/
├── infrastructure/
├── repositories/
├── services/
├── workflows/
├── agents/
├── prompts/
├── rag/
├── embeddings/
├── storage/
├── guardrails/
├── validators/
├── telemetry/
├── jobs/
└── main.py
```

This structure separates business concerns from implementation details and supports future extraction into independent services.

---

# Alternatives Considered

## Option 1 — Layered MVC

### Advantages

- Simple
- Familiar

### Disadvantages

- Business logic leaks into controllers
- Difficult to test independently
- Tight framework coupling
- Poor fit for AI workflows

**Decision:** Rejected

---

## Option 2 — Feature-Based Structure

### Advantages

- Fast initial development
- Easy for small projects

### Disadvantages

- Shared business logic becomes duplicated
- Hard to enforce boundaries
- Infrastructure concerns leak into features

**Decision:** Rejected

---

## Option 3 — Clean Architecture + Hexagonal Boundaries

### Advantages

- Framework-independent
- Highly testable
- Modular
- Scalable
- Supports dependency inversion
- Enables provider replacement
- Supports AI guardrails
- Simplifies future microservice extraction
- Long-term maintainability

### Disadvantages

- More initial boilerplate
- Higher learning curve
- Additional abstractions

**Decision:** Accepted

---

# Consequences

## Positive

- Clear separation of concerns
- Easier unit testing
- Better maintainability
- Infrastructure can be replaced with minimal changes
- Supports future microservices
- Encourages reusable business logic
- Enables deterministic validation
- Enables centralized guardrails
- Improves observability

---

## Negative

- More files
- Additional abstractions
- Slightly slower initial development
- Requires discipline during code reviews

The long-term benefits outweigh the initial complexity.

---

# Risks

| Risk                  | Mitigation                               |
| --------------------- | ---------------------------------------- |
| Over-engineering      | Keep abstractions practical              |
| Excessive boilerplate | Reuse common patterns                    |
| Team unfamiliarity    | Document architecture and examples       |
| Layer violations      | Enforce through code reviews and linters |
| Interface explosion   | Introduce ports only when needed         |
| Guardrail duplication | Centralize guardrail policies            |

---

# Impact

This decision influences:

- API Design
- Workflow Engine
- Repository Layer
- Database Access
- RAG Pipeline
- Guardrails Engine
- Validation Engine
- Testing Strategy
- Deployment
- Observability
- Future Microservices

Every backend component must follow this architectural pattern.

---

# Migration Strategy

Tailr will evolve through the following stages.

## Phase 1 — Modular Monolith (Current)

- Single FastAPI application
- Internal modules follow Clean Architecture
- Shared database and vector store

## Phase 2 — Extract RAG Service

- Independent retrieval service
- Separate scaling characteristics

## Phase 3 — Extract Agent Service

- Dedicated workflow workers
- Asynchronous execution

## Phase 4 — Event-Driven Architecture

- Kafka / Redis Streams
- Independent service deployment

The current architecture is intentionally designed to make these transitions incremental rather than requiring a rewrite.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0003 — Use FastAPI as the Web Framework
- ADR-0004 — Use PostgreSQL as the Primary Database
- ADR-0005 — Use Qdrant as the Vector Database
- ADR-0006 — Adopt a Multi-Agent Workflow
- ADR-0008 — Adopt a Validation & Guardrails Engine

---

# References

- system-architecture.md
- database-design.md
- api-specification.md
- workflow-design.md
- testing.md
- guardrails-architecture.md

---

# Review Notes

This ADR should be revisited if:

- the application is fully decomposed into independent microservices,
- domain boundaries change significantly,
- architectural complexity outweighs its benefits, or
- a different architectural style provides substantially better support for AI-native workflows.

Until then, **Clean Architecture with Hexagonal boundaries remains the standard backend architecture for Tailr**.

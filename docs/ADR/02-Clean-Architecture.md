# ADR-0002: Adopt Clean Architecture for the Backend

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr is not a CRUD application.

The platform consists of multiple independent components:

- Resume Parser
- Knowledge Builder
- RAG Engine
- Multi-Agent Workflow
- Validation Engine
- ATS Scoring
- PDF Renderer
- Version Manager

These components interact with databases, vector stores, LLMs, object storage, and external services.

Without clear architectural boundaries, business logic would become tightly coupled to frameworks and infrastructure, making testing, maintenance, and future evolution difficult.

The system requires an architecture that:

- isolates business rules
- enables dependency inversion
- supports unit testing
- allows infrastructure replacement
- scales as new AI capabilities are added

---

# Decision

Tailr adopts **Clean Architecture** with selected **Domain-Driven Design (DDD)** principles.

The application is organized into independent layers.

```
                Presentation Layer
        (FastAPI, REST API, WebSocket)
                     │
                     ▼
            Application Layer
      (Use Cases / Orchestrators)
                     │
                     ▼
              Domain Layer
      (Business Rules & Entities)
                     │
                     ▼
           Infrastructure Layer
(PostgreSQL, Qdrant, Redis, Ollama)
```

Dependencies always point inward.

The Domain layer must not depend on FastAPI, SQLAlchemy, Qdrant, or any external library.

---

# Decision Drivers

The architecture should:

- separate business logic from infrastructure
- simplify testing
- support AI workflow orchestration
- allow multiple storage backends
- enable future microservices
- reduce framework lock-in

---

# Layer Responsibilities

## Presentation Layer

Responsible for:

- HTTP APIs
- Authentication
- Request validation
- Response serialization

No business logic exists here.

---

## Application Layer

Responsible for:

- Workflow orchestration
- Transactions
- Use cases
- Coordination between services

Examples

- Optimize Resume
- Analyze Job Description
- Generate ATS Report

---

## Domain Layer

Contains:

- Resume entity
- Job Description entity
- Validation rules
- ATS scoring rules
- Business policies

This layer contains the core business knowledge.

---

## Infrastructure Layer

Responsible for:

- PostgreSQL
- Redis
- Qdrant
- Ollama
- File storage
- PDF generation
- External APIs

Infrastructure can change without affecting business logic.

---

# Repository Pattern

Application services communicate through interfaces.

Example

```
ResumeRepository

KnowledgeRepository

WorkflowRepository

PromptRepository
```

Infrastructure provides implementations.

---

# Dependency Rule

Allowed

```
Presentation

↓

Application

↓

Domain
```

Forbidden

```
Domain

↓

FastAPI
```

```
Domain

↓

SQLAlchemy
```

```
Domain

↓

Qdrant
```

The Domain layer remains framework-independent.

---

# Project Structure

```
backend/

app/

├── api/
├── application/
├── domain/
├── infrastructure/
├── repositories/
├── services/
├── workflows/
├── agents/
├── prompts/
├── validators/
└── main.py
```

This structure separates business concerns from implementation details.

---

# Alternatives Considered

## Option 1 — Layered MVC

Advantages

- Simple
- Familiar

Disadvantages

- Business logic often leaks into controllers
- Difficult to test independently
- Tight framework coupling

Decision: Rejected

---

## Option 2 — Feature-Based Structure

Advantages

- Easy for small projects
- Fast development

Disadvantages

- Shared business logic becomes duplicated
- Harder to enforce architectural boundaries

Decision: Rejected

---

## Option 3 — Clean Architecture

Advantages

- Framework-independent
- Highly testable
- Modular
- Scalable
- Supports dependency inversion
- Long-term maintainability

Disadvantages

- More initial boilerplate
- Higher learning curve

Decision: Accepted

---

# Consequences

## Positive

- Clear separation of concerns
- Easier unit testing
- Better maintainability
- Replace infrastructure with minimal changes
- Supports future microservices
- Encourages reusable business logic

---

## Negative

- More files
- Additional abstractions
- Slightly slower initial development

The long-term benefits outweigh the initial complexity.

---

# Risks

| Risk                  | Mitigation                         |
| --------------------- | ---------------------------------- |
| Over-engineering      | Keep abstractions practical        |
| Excessive boilerplate | Reuse common patterns              |
| Team unfamiliarity    | Document architecture and examples |
| Layer violations      | Enforce through code reviews       |

---

# Impact

This decision influences:

- API Design
- Workflow Engine
- Repository Layer
- Database Access
- Testing Strategy
- Deployment
- Future Microservices

Every backend component follows this architectural pattern.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0003 — Use FastAPI as the Web Framework
- ADR-0004 — Use PostgreSQL as the Primary Database
- ADR-0005 — Use Qdrant as the Vector Database
- ADR-0006 — Adopt a Multi-Agent Workflow

---

# References

- System-Architecture.md
- Database-Design.md
- API-Specification.md
- Workflow-Design.md
- Testing.md

---

# Review Notes

This ADR should be revisited if:

- the application is split into independent microservices,
- domain boundaries change significantly, or
- architectural complexity outweighs its benefits.

Until then, Clean Architecture remains the standard backend architecture for Tailr.

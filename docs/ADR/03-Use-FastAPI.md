# ADR-0003: Use FastAPI as the Primary Backend Framework

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr is an AI-native backend that orchestrates multiple subsystems including:

- Resume Parser
- Knowledge Layer
- RAG Pipeline
- Multi-Agent Workflow
- Guardrails Engine
- Validation Engine
- ATS Engine
- Rendering Engine
- Object Storage
- Vector Database
- Background Workers
- Evaluation Pipeline

The backend primarily exposes REST APIs that coordinate long-running AI workflows and asynchronous processing.

The framework must provide:

- High performance
- Strong type safety
- Automatic validation
- Asynchronous execution
- Automatic API documentation
- Dependency injection
- WebSocket support
- Easy integration with modern AI libraries
- Production readiness
- OpenTelemetry compatibility

Several Python web frameworks were evaluated.

---

# Decision

Tailr will use **FastAPI** as its primary backend framework.

FastAPI is responsible for:

- REST APIs
- Authentication and authorization
- Request validation
- Response serialization
- Dependency injection
- OpenAPI generation
- WebSocket endpoints
- Streaming responses
- Health and readiness endpoints
- Background task coordination

Business logic remains inside the **Application** and **Domain** layers defined in ADR-0002.

FastAPI acts strictly as the **Presentation Layer** in the Clean/Hexagonal Architecture.

---

# Decision Drivers

The framework must:

- support asynchronous programming,
- provide automatic request validation,
- integrate naturally with Pydantic v2,
- generate OpenAPI documentation,
- support dependency injection,
- scale to production workloads,
- work well with AI and ML ecosystems,
- support observability and tracing,
- enforce guardrails consistently.

---

# Why FastAPI?

FastAPI provides:

- Async-first architecture
- Native Python type hints
- Automatic request parsing
- Automatic OpenAPI documentation
- Pydantic v2 validation
- High performance through ASGI
- Excellent developer experience
- Strong ecosystem support for AI applications

Example endpoint:

<CodeBlock language="python" content="from uuid import UUID
from fastapi import APIRouter

router = APIRouter()

@router.post("/optimize")
async def optimize_resume(request: OptimizeResumeRequest):
return await optimize_use_case.execute(request)"/>

Minimal boilerplate improves maintainability and readability.

---

# Architectural Role

<CodeBlock language="text" content="Next.js Frontend
     │
     ▼
   FastAPI
     │
     ▼
Application Layer
     │
     ▼
Ports / Interfaces
     │
     ▼
Domain Layer
     ▲
     │
Infrastructure Adapters"/>

FastAPI contains **no business logic**.

It only coordinates requests, responses, authentication, and dependency wiring.

---

# Async Support

Many Tailr operations are I/O bound.

Examples:

- Reading LaTeX files
- Querying PostgreSQL
- Searching Qdrant
- Calling Ollama
- Uploading artifacts
- Writing PDFs
- Exporting telemetry

Async execution allows these operations to run efficiently without blocking worker threads.

FastAPI runs on **Uvicorn + ASGI**, enabling high concurrency with low overhead.

---

# Request Validation

FastAPI uses **Pydantic v2** models.

<CodeBlock language="python" content="from pydantic import BaseModel
from uuid import UUID

class OptimizeResumeRequest(BaseModel):
resume_id: UUID
job_description: str"/>

Benefits:

- Automatic validation
- Type safety
- Clear API contracts
- Better editor support
- Reduced boilerplate
- Automatic error responses

---

# Structured Responses

All APIs return typed response models.

<CodeBlock language="python" content="class OptimizeResumeResponse(BaseModel):
 workflow_id: UUID
 status: str
 ats_score: float
 download_url: str"/>

This ensures:

- deterministic API behavior,
- generated SDK compatibility,
- easier frontend integration,
- schema evolution control.

---

# Automatic API Documentation

FastAPI automatically generates:

- OpenAPI Specification
- Swagger UI
- ReDoc

This enables:

- interactive API exploration,
- frontend development,
- automated testing,
- SDK generation,
- external API documentation.

No manual OpenAPI maintenance is required.

---

# Dependency Injection

FastAPI provides lightweight dependency injection.

<CodeBlock language="python" content="from fastapi import Depends

def get_resume_service() -> ResumeService:
return ResumeService(...)

@router.get("/resumes/{resume_id}")
async def get_resume(
resume_id: UUID,
service: ResumeService = Depends(get_resume_service),
):
return await service.get(resume_id)"/>

Benefits:

- easier testing,
- loose coupling,
- configurable implementations,
- environment-specific wiring.

---

# Streaming Responses

Resume optimization can take several seconds.

FastAPI supports:

- Server-Sent Events (SSE)
- StreamingResponse
- WebSockets

This enables real-time progress updates:

<CodeBlock language="text" content="Parsing → Indexing → Planning → Rewriting → Guardrails → Validation → Rendering → Completed"/>

Streaming improves user experience for long-running workflows.

---

# Background Processing

Heavy operations are executed outside the request lifecycle.

Examples:

- embedding generation,
- PDF rendering,
- benchmark evaluation,
- cleanup jobs,
- notification delivery.

FastAPI integrates well with future worker systems such as:

- ARQ
- Dramatiq
- Celery
- Redis Queue

The API remains responsive while asynchronous jobs execute independently.

---

# Guardrails Integration

Every AI request passes through the Guardrails layer before business validation.

FastAPI is responsible for:

- propagating request IDs,
- attaching user context,
- enforcing authentication,
- validating uploaded files,
- forwarding structured requests to workflows.

Guardrails remain inside the Application layer and are **not implemented as FastAPI middleware**.

---

# Observability

FastAPI integrates with **OpenTelemetry**.

Collected telemetry includes:

- request latency,
- workflow duration,
- token usage,
- guardrail violations,
- database query timing,
- external provider latency,
- error rates.

This telemetry is exported to Prometheus/Grafana and future tracing backends.

---

# Alternatives Considered

## Option 1 — Flask

### Advantages

- Simple
- Large ecosystem
- Lightweight

### Disadvantages

- Manual validation
- Limited async support
- More boilerplate
- Requires additional libraries
- Weaker typing guarantees

**Decision:** Rejected

---

## Option 2 — Django

### Advantages

- Batteries included
- Mature ecosystem
- Built-in admin panel

### Disadvantages

- Heavyweight
- ORM-centric
- More suited for traditional web applications
- Unnecessary complexity for AI services
- Harder to keep the Domain layer framework-independent

**Decision:** Rejected

---

## Option 3 — FastAPI

### Advantages

- High performance
- Async-first
- Type-safe
- Automatic documentation
- Excellent AI ecosystem support
- Clean developer experience
- Natural fit for Pydantic-based schemas
- Strong OpenTelemetry support

### Disadvantages

- Smaller ecosystem than Django
- Async programming requires discipline
- Some third-party libraries remain synchronous

**Decision:** Accepted

---

# Consequences

## Positive

- High throughput
- Strong validation
- Automatic documentation
- Excellent testing support
- Modern async architecture
- Better developer productivity
- Easier frontend integration
- Cleaner API contracts

---

## Negative

- Requires understanding of async programming
- Blocking synchronous code can hurt performance
- Additional care is needed for thread safety
- Background job infrastructure adds operational complexity

---

# Risks

| Risk                                     | Mitigation                                       |
| ---------------------------------------- | ------------------------------------------------ |
| Blocking synchronous code                | Use async-compatible libraries whenever possible |
| Complex dependency graph                 | Follow ADR-0002 and dependency injection         |
| Large API surface                        | Organize endpoints by feature modules            |
| Long-running requests                    | Offload heavy work to background workers         |
| Accidental business logic in controllers | Enforce code review rules                        |
| Unbounded streaming connections          | Configure timeouts and connection limits         |

---

# API Organization

Endpoints are organized by feature.

<CodeBlock language="text" content="api/
├── resumes/
├── jobs/
├── workflows/
├── ats/
├── prompts/
├── evaluations/
├── guardrails/
└── health/"/>

This structure keeps the presentation layer modular and aligned with application use cases.

---

# Impact

This decision affects:

- API Specification
- Authentication & Authorization
- Request Validation
- WebSocket Support
- Streaming Responses
- Background Processing
- OpenAPI Documentation
- Frontend Integration
- Observability
- Deployment Architecture

FastAPI becomes the **public interface of the Tailr backend**.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture with Hexagonal Boundaries
- ADR-0004 — Use PostgreSQL as the Primary Database
- ADR-0005 — Use Qdrant as the Vector Database
- ADR-0006 — Adopt a Multi-Agent Workflow
- ADR-0008 — Adopt a Validation & Guardrails Engine

---

# References

- api-specification.md
- system-architecture.md
- deployment.md
- testing.md
- guardrails-architecture.md
- telemetry-architecture.md

---

# Review Notes

This decision should be revisited if:

- the application requires protocols beyond HTTP and WebSockets,
- framework limitations significantly impact development,
- organizational requirements mandate a different framework,
- or the backend is decomposed into services with different runtime requirements.

At present, **FastAPI provides the best balance of performance, developer productivity, type safety, and compatibility with AI-native workloads**, making it the preferred backend framework for Tailr.

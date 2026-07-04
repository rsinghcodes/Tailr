# ADR-0003: Use FastAPI as the Primary Backend Framework

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr is an AI-native backend that orchestrates multiple services including:

- Resume Parser
- Multi-Agent Workflow
- RAG Pipeline
- ATS Engine
- Validation Engine
- PDF Renderer
- Object Storage
- Vector Database
- Background Jobs

The backend primarily exposes REST APIs that coordinate long-running AI workflows.

The framework must provide:

- High performance
- Strong type safety
- Automatic validation
- Asynchronous execution
- Automatic API documentation
- Easy integration with modern AI libraries
- Production readiness

Several Python web frameworks were evaluated.

---

# Decision

Tailr will use **FastAPI** as its primary backend framework.

FastAPI will be responsible for:

- REST APIs
- Authentication
- Request validation
- Dependency injection
- OpenAPI generation
- WebSocket endpoints
- Background task orchestration

Business logic will remain inside the Application and Domain layers defined in ADR-0002.

FastAPI serves as the presentation layer only.

---

# Decision Drivers

The framework should:

- Support asynchronous programming
- Provide automatic request validation
- Integrate naturally with Pydantic
- Generate OpenAPI documentation
- Offer excellent developer experience
- Scale to production workloads
- Work well with AI and ML ecosystems

---

# Why FastAPI?

FastAPI provides:

- Async-first architecture
- Native type hints
- Automatic request parsing
- Automatic OpenAPI documentation
- Pydantic-based validation
- High performance via ASGI
- Strong ecosystem support

Example endpoint:

```python
@router.post("/optimize")
async def optimize_resume(request: OptimizeRequest):
    return await optimize_use_case.execute(request)
```

Minimal boilerplate improves maintainability.

---

# Architectural Role

```
React Frontend
        │
        ▼
     FastAPI
        │
        ▼
Application Layer
        │
        ▼
Domain Layer
        │
        ▼
Infrastructure
```

FastAPI does not contain business logic.

It simply coordinates requests and responses.

---

# Async Support

Many Tailr operations are I/O bound.

Examples:

- Reading LaTeX files
- Querying PostgreSQL
- Searching Qdrant
- Calling Ollama
- Writing PDFs
- Uploading artifacts

Async execution allows these operations to run efficiently without blocking worker threads.

---

# Request Validation

FastAPI uses Pydantic models.

Example:

```python
class OptimizeResumeRequest(BaseModel):
    resume_id: UUID
    job_description: str
```

Benefits

- Automatic validation
- Type safety
- Clear API contracts
- Reduced boilerplate

---

# Automatic API Documentation

FastAPI generates:

- OpenAPI Specification
- Swagger UI
- ReDoc

This enables:

- Easy frontend integration
- API testing
- SDK generation
- External documentation

No manual API documentation is required.

---

# Dependency Injection

FastAPI provides lightweight dependency injection.

Example:

```python
def get_resume_service():
    return ResumeService(...)
```

Benefits

- Easier testing
- Loose coupling
- Configurable implementations

---

# Background Tasks

Tailr performs several long-running operations.

Examples

- Resume optimization
- Embedding generation
- PDF rendering
- ATS analysis

FastAPI integrates well with background workers such as:

- ARQ
- Celery
- Dramatiq

The API remains responsive while background jobs execute asynchronously.

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

Decision: Rejected

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

Decision: Rejected

---

## Option 3 — FastAPI

### Advantages

- High performance
- Async-first
- Type-safe
- Automatic documentation
- Excellent AI ecosystem support
- Clean developer experience

### Disadvantages

- Smaller ecosystem than Django
- Async programming requires discipline

Decision: Accepted

---

# Consequences

## Positive

- High throughput
- Strong validation
- Automatic documentation
- Excellent testing support
- Modern async architecture
- Better developer productivity

---

## Negative

- Requires understanding of async programming
- Some third-party libraries remain synchronous
- Additional care needed to avoid blocking operations

---

# Risks

| Risk                      | Mitigation                                         |
| ------------------------- | -------------------------------------------------- |
| Blocking synchronous code | Use async-compatible libraries wherever possible   |
| Complex dependency graph  | Follow Clean Architecture and dependency injection |
| Large API surface         | Organize endpoints by feature modules              |
| Long-running requests     | Offload heavy work to background workers           |

---

# Impact

This decision affects:

- API Specification
- Authentication
- Request Validation
- WebSocket Support
- Background Processing
- API Documentation
- Frontend Integration
- Deployment

FastAPI becomes the public interface of the Tailr backend.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture
- ADR-0004 — Use PostgreSQL as the Primary Database
- ADR-0005 — Use Qdrant as the Vector Database
- ADR-0006 — Use LlamaIndex for RAG

---

# References

- API-Specification.md
- System-Architecture.md
- Deployment.md
- Testing.md

---

# Review Notes

This decision should be revisited if:

- the application requires protocols beyond HTTP/WebSockets,
- framework limitations significantly impact development, or
- organizational requirements favor a different backend framework.

At present, FastAPI provides the best balance of performance, developer productivity, and compatibility with AI-native workloads.

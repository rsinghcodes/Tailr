# Resume Domain — Production Implementation Prompt

## Objective

Implement the complete production-ready **Resume Domain** for Tailr.

This domain encapsulates all business logic, entities, value objects, services, repositories, and API schemas related to resume management.

The Resume Domain is responsible for:

- the Canonical Resume Model,
- resume lifecycle management,
- resume versioning,
- domain events,
- domain services,
- repository interfaces,
- application services,
- API schemas,
- typed exceptions,
- and guardrail-aware persistence.

The domain layer must contain **no infrastructure code**.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/database.md
- rules/testing.md
- rules/logging.md
- rules/security.md
- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture
- ADR-0004 — Use PostgreSQL
- ADR-0011 — Validation & Guardrails Engine
- 05-Data-Models.md
- 07-Parser-Architecture.md
- 09-Guardrails-Architecture.md
- 13-Database-Design.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Architecture Constraints

## Domain Layer Rules

The domain layer must never import:

- FastAPI
- SQLAlchemy
- HTTP clients
- LLM clients
- the Guardrails Engine directly

Domain entities and policies define _what_ is immutable or valid.

The Application layer is responsible for invoking Guardrails before domain state is mutated.

## Separation of Models

Maintain strict separation:

- **ORM Models** — infrastructure only, never leave repositories
- **Domain Models** — business logic, used by services
- **API Schemas** — request/response only, used by routers

Never reuse one object for all layers.

---

# Domain Models

Implement the Canonical Resume Model as defined in ADR-0001 and 05-Data-Models.md.

---

## Resume Entity

```python
Resume(
    id: ResumeId,
    user_id: UserId,
    summary: ResumeSummary,
    experience: list[Experience],
    projects: list[Project],
    skills: list[SkillCategory],
    education: list[Education],
    certifications: list[Certification],
    achievements: list[Achievement],
    metadata: ResumeMetadata,
    version: int,
    created_at: datetime,
    updated_at: datetime,
)
```

### Behavior

- `calculate_completeness_score()` — assess resume completeness
- `get_technologies()` — extract all technologies across sections
- `get_keywords()` — extract all keywords for ATS
- `normalize_skills()` — deduplicate and normalize skill names
- `remove_duplicates()` — remove duplicate entries across sections
- `validate_integrity()` — check required fields and consistency

Business logic belongs inside entities or domain services.

---

## Value Objects

Implement immutable value objects:

- `ResumeSummary` — text, keywords, word_count
- `Experience` — company, role, location, employment_type, start_date, end_date, technologies, bullets, achievements
- `ExperienceBullet` — text, metrics, keywords, priority
- `Project` — title, description, technologies, repository, demo, bullets, category
- `SkillCategory` — category, skills
- `Skill` — name, category, years, proficiency, verified
- `Education` — institution, degree, field, cgpa, start_date, end_date
- `Certification` — name, issuer, credential_id, issue_date
- `Achievement` — title, description, category, date
- `ResumeMetadata` — template, source_file, parse_version, schema_version

Value objects must use equality by value.

---

## Immutable Facts

The following fields are immutable and protected by Guardrails:

- employer names
- project names
- education institutions
- degrees
- employment dates
- certifications

Guardrails is the first line of defense; domain invariants are the last line of defense.

---

# Domain Services

Implement domain services for cross-entity operations.

## ResumeIntegrityService

- verify no hallucinated employers
- verify no hallucinated projects
- verify no fabricated metrics
- verify no altered dates
- compare optimized resume against canonical model

## ResumeScoringService

- calculate completeness score
- calculate keyword coverage
- calculate ATS readiness score

## ResumeVersioningService

- create new version from optimized content
- compare versions
- restore previous version
- track version history

---

# Repository Interfaces

Define repository ports in the domain/application layer.

## ResumeRepository (Port)

```python
class ResumeRepository(Protocol):
    async def get_by_id(self, resume_id: ResumeId) -> Resume | None: ...
    async def get_by_user_id(self, user_id: UserId, pagination: PaginationParams) -> PaginatedResult[Resume]: ...
    async def create(self, resume: Resume) -> Resume: ...
    async def update(self, resume: Resume) -> Resume: ...
    async def delete(self, resume_id: ResumeId) -> None: ...
    async def exists(self, resume_id: ResumeId) -> bool: ...
    async def count_by_user(self, user_id: UserId) -> int: ...
```

## ResumeVersionRepository (Port)

```python
class ResumeVersionRepository(Protocol):
    async def create_version(self, version: ResumeVersion) -> ResumeVersion: ...
    async def get_versions(self, resume_id: ResumeId) -> list[ResumeVersion]: ...
    async def get_version(self, resume_id: ResumeId, version: int) -> ResumeVersion | None: ...
    async def restore_version(self, resume_id: ResumeId, version: int) -> Resume: ...
```

### Repository Rules

Repositories must:

- accept `AsyncSession`,
- return domain entities,
- never commit automatically,
- never contain business logic,
- never accept AI-generated content without a `GuardrailResult` proving it was approved or repaired.

---

# Application Services

Implement use-case orchestrators.

## ResumeApplicationService

- `upload_resume(file, user_id)` — validate, parse, store, index
- `get_resume(resume_id, user_id)` — fetch with authorization
- `list_resumes(user_id, pagination)` — paginated listing
- `delete_resume(resume_id, user_id)` — soft delete with authorization
- `get_versions(resume_id, user_id)` — list versions
- `restore_version(resume_id, version, user_id)` — restore specific version
- `store_optimized_resume(resume_id, optimized_content, guardrail_result)` — persist only if guardrail status is `approved` or `repaired`

### Guardrails Integration

Every use case that stores AI-generated resume content must:

1. verify `GuardrailResult.status` is `approved` or `repaired`,
2. persist the content and guardrail audit events in the same transaction,
3. raise `GuardrailRejectionError` if status is `rejected`.

---

# Domain Events

Implement domain events:

- `ResumeUploaded`
- `ResumeParsed`
- `ResumeOptimized`
- `ResumeVersionCreated`
- `ResumeDeleted`
- `ResumeRestored`

Each event must include:

- event_id
- occurred_at
- aggregate_id (resume_id)
- user_id
- metadata

---

# Typed Exceptions

- `ResumeNotFoundError`
- `ResumeParsingError`
- `ResumeValidationError`
- `ResumeVersionNotFoundError`
- `ResumeIntegrityError`
- `DuplicateResumeError`

All exceptions must map to standardized API responses with HTTP status codes.

---

# API Schemas

Implement Pydantic v2 schemas for the API layer.

## Request Schemas

- `UploadResumeRequest` — file, template_name
- `UpdateResumeRequest` — partial update fields
- `RestoreVersionRequest` — version number

## Response Schemas

- `ResumeResponse` — full resume with metadata
- `ResumeSummaryResponse` — lightweight listing
- `ResumeVersionResponse` — version metadata
- `ResumeVersionListResponse` — paginated versions

---

# Required File Structure

Generate production-ready files:

```text
domain/
├── resume/
│   ├── __init__.py
│   ├── entities.py
│   ├── value_objects.py
│   ├── services.py
│   ├── events.py
│   ├── exceptions.py
│   └── ports.py

application/
├── resume/
│   ├── __init__.py
│   ├── service.py
│   └── dto.py

infrastructure/
├── repositories/
│   ├── resume_repository.py
│   └── resume_version_repository.py
├── models/
│   └── resume.py

api/
├── schemas/
│   ├── requests/
│   │   └── resume.py
│   └── responses/
│       └── resume.py
├── routers/
│   └── resume.py
└── dependencies/
    └── resume.py
```

---

# Testing Requirements

Generate tests for:

- entity behavior (completeness score, keyword extraction, normalization),
- value object equality and immutability,
- domain service integrity checks,
- repository CRUD operations,
- application service use cases,
- guardrail-gated persistence (approved, repaired, rejected paths),
- domain event emission,
- exception serialization,
- API schema validation,
- router endpoints,
- versioning (create, list, restore),
- authorization (owner vs non-owner),
- and pagination.

Use:

- pytest
- pytest-asyncio
- Testcontainers (integration tests)
- factories for test data generation

Target coverage: **90%+** for domain and application modules.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings for public classes and functions,
- separate domain from infrastructure,
- follow DDD patterns,
- be async-first,
- and be production deployable.

### Additional Constraints

- no TODO placeholders,
- no SQLAlchemy imports in domain layer,
- no FastAPI imports in domain layer,
- no raw AI output persisted without guardrail approval,
- and no ORM models returned from services.

---

# Output Requirements

Return:

1. complete production-ready source files,
2. test files,
3. domain model diagram,
4. entity relationship explanation,
5. versioning strategy explanation,
6. guardrail integration explanation,
7. repository pattern explanation,
8. API schema examples,
9. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Resume Domain** that provides:

- a canonical resume model,
- domain-driven design,
- full entity behavior,
- versioning support,
- guardrail-aware persistence,
- clean separation of layers,
- and comprehensive testing

for the entire Tailr platform.

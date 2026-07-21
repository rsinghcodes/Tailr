# Job Description Domain — Production Implementation Prompt

## Objective

Implement the complete production-ready **Job Description Domain** for Tailr.

This domain encapsulates all business logic, entities, value objects, services, repositories, and API schemas related to job description management and analysis.

The Job Description Domain is responsible for:

- job description storage,
- JD analysis (AI-powered extraction),
- structured job requirements model,
- repository interfaces,
- application services,
- API schemas,
- domain events,
- typed exceptions,
- and guardrail-validated analysis output.

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
- rules/ai-agents.md
- ADR-0002 — Clean Architecture
- ADR-0006 — Adopt Multi-Agent Architecture
- ADR-0008 — Model Provider Abstraction
- ADR-0011 — Validation & Guardrails Engine
- 02-Agent-Architecture.md
- 05-Data-Models.md
- 11-API-Specification.md
- 09-Guardrails-Architecture.md

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

JD analysis uses an AI agent (JD Analyzer), but the domain layer defines the _output schema_ — the AI provider and guardrail orchestration live in the Application and Infrastructure layers.

---

# Domain Models

Implement the Job Description models as defined in 05-Data-Models.md.

---

## JobDescription Entity

```python
JobDescription(
    id: JobDescriptionId,
    user_id: UserId,
    title: str,
    company: str | None,
    location: str | None,
    employment_type: EmploymentType | None,
    raw_text: str,
    requirements: JobRequirements | None,
    analysis_status: AnalysisStatus,
    metadata: JobDescriptionMetadata,
    created_at: datetime,
    updated_at: datetime,
)
```

### Behavior

- `is_analyzed()` — check if requirements have been extracted
- `get_all_skills()` — combine required and preferred skills
- `get_keyword_set()` — extract unique keywords for matching
- `calculate_complexity()` — estimate JD complexity based on requirements count

---

## JobRequirements Value Object

```python
JobRequirements(
    required_skills: list[str],
    preferred_skills: list[str],
    responsibilities: list[str],
    soft_skills: list[str],
    keywords: list[str],
    experience_level: ExperienceLevel,
    certifications: list[str],
    education_requirements: list[str],
    guardrail_status: GuardrailStatus,
)
```

### Constraints

- `JobRequirements` can only be constructed after the JD Analyzer output has passed through Guardrails with `approved` or `repaired` status.
- The `guardrail_status` field records the validation outcome.

---

## Supporting Value Objects

- `ExperienceLevel` — enum: entry, mid, senior, lead, principal, executive
- `EmploymentType` — enum: full_time, part_time, contract, internship, freelance
- `AnalysisStatus` — enum: pending, analyzing, completed, failed
- `JobDescriptionMetadata` — source, word_count, language, analyzed_at, model_used, prompt_version

---

# Domain Services

## JDMatchingService

- `calculate_skill_match(resume, job_requirements)` — compute overlap between resume skills and JD requirements
- `identify_missing_skills(resume, job_requirements)` — list skills in JD not found in resume
- `calculate_keyword_coverage(resume, job_requirements)` — percentage of JD keywords present in resume

## JDNormalizationService

- normalize skill names (e.g., "JS" → "JavaScript")
- deduplicate skills
- categorize skills by domain

---

# Repository Interfaces

## JobDescriptionRepository (Port)

```python
class JobDescriptionRepository(Protocol):
    async def get_by_id(self, jd_id: JobDescriptionId) -> JobDescription | None: ...
    async def get_by_user_id(self, user_id: UserId, pagination: PaginationParams) -> PaginatedResult[JobDescription]: ...
    async def create(self, jd: JobDescription) -> JobDescription: ...
    async def update(self, jd: JobDescription) -> JobDescription: ...
    async def delete(self, jd_id: JobDescriptionId) -> None: ...
```

---

# Application Services

## JDApplicationService

- `analyze_job_description(text, user_id)` — store raw text, invoke JD Analyzer agent, run Guardrails on output, persist structured requirements
- `get_job_description(jd_id, user_id)` — fetch with authorization
- `list_job_descriptions(user_id, pagination)` — paginated listing
- `delete_job_description(jd_id, user_id)` — soft delete
- `compare_with_resume(jd_id, resume_id, user_id)` — compute skill match and keyword coverage

### Guardrails Integration

The JD analysis output is AI-generated and must pass through Guardrails with `analysis_standard` profile before persistence.

1. JD Analyzer agent produces structured output.
2. Guardrails validates: JSON structure, schema compliance, prompt injection detection.
3. If `approved` or `repaired`, persist `JobRequirements`.
4. If `rejected`, raise `GuardrailRejectionError`.

---

# Domain Events

- `JobDescriptionCreated`
- `JobDescriptionAnalyzed`
- `JobDescriptionDeleted`
- `AnalysisFailed`

Each event must include: event_id, occurred_at, aggregate_id, user_id, metadata.

---

# Typed Exceptions

- `JobDescriptionNotFoundError`
- `JobDescriptionAnalysisError`
- `JobDescriptionValidationError`
- `DuplicateJobDescriptionError`

---

# API Schemas

## Request Schemas

- `AnalyzeJobDescriptionRequest` — text (required), title (optional), company (optional)
- `CompareWithResumeRequest` — resume_id, job_description_id

## Response Schemas

- `JobDescriptionResponse` — full JD with requirements
- `JobDescriptionSummaryResponse` — lightweight listing
- `SkillMatchResponse` — match percentage, missing skills, keyword coverage

---

# Required File Structure

```text
domain/
├── job/
│   ├── __init__.py
│   ├── entities.py
│   ├── value_objects.py
│   ├── services.py
│   ├── events.py
│   ├── exceptions.py
│   └── ports.py

application/
├── job/
│   ├── __init__.py
│   ├── service.py
│   └── dto.py

infrastructure/
├── repositories/
│   └── job_description_repository.py
├── models/
│   └── job_description.py

api/
├── schemas/
│   ├── requests/
│   │   └── job.py
│   └── responses/
│       └── job.py
├── routers/
│   └── job.py
└── dependencies/
    └── job.py
```

---

# Testing Requirements

Generate tests for:

- entity behavior (is_analyzed, skill extraction, keyword coverage),
- value object immutability,
- domain service matching logic,
- repository CRUD operations,
- application service analysis flow (approved, repaired, rejected),
- guardrail-gated persistence,
- domain event emission,
- exception serialization,
- API schema validation,
- router endpoints,
- authorization checks,
- and pagination.

Use: pytest, pytest-asyncio, Testcontainers, factories.

Target coverage: **90%+**.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- separate domain from infrastructure,
- follow DDD patterns,
- be async-first,
- and be production deployable.

---

# Output Requirements

Return:

1. complete source files,
2. test files,
3. domain model diagram,
4. analysis flow explanation,
5. guardrail integration explanation,
6. skill matching algorithm explanation,
7. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Job Description Domain** that provides:

- structured JD analysis,
- domain-driven design,
- guardrail-validated AI output,
- skill matching,
- clean separation of layers,
- and comprehensive testing

for the Tailr platform.

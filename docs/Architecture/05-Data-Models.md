# Data Models

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the canonical data models used throughout Tailr.

These models establish a common language shared by every component in the system.

Every module—including the parser, knowledge builder, agents, validators, renderer, APIs, and database—communicates using these strongly typed models.

The objectives are:

- Eliminate ambiguity
- Ensure deterministic processing
- Simplify validation
- Enable modular development
- Improve maintainability

---

# 2. Design Principles

The data model follows several engineering principles.

## Strong Typing

Every object has a well-defined schema.

No component exchanges raw dictionaries or free-form JSON.

---

## Immutable Facts

Professional facts never change.

Examples

- employer
- project name
- degree
- dates

---

## Mutable Presentation

Presentation may evolve.

Examples

- summary
- bullet wording
- ordering
- emphasis

---

## Validation First

Every model validates itself before entering the workflow.

---

## Explicit Relationships

Models reference one another through identifiers rather than nested arbitrary objects whenever possible.

---

## Policy Enforcement

Every model is protected by deterministic Guardrail policies.

Domain models define the data.

Guardrails define what may or may not change.

This separation keeps business logic independent from AI reasoning while preserving data integrity.

---

# 3. Model Categories

```
                    Data Models
                         │
      ┌──────────────────┼──────────────────┬─────────────────┐
      │                  │                  │                 │
      ▼                  ▼                  ▼                 ▼
 Domain Models     Workflow Models    API Models     Guardrail Models
      │                  │                  │                 │
      ▼                  ▼                  ▼                 ▼
Agent Contracts   Database Models   Vector Metadata   Policy Models
```

---

# 4. Base Model

Every entity inherits common metadata.

```python
BaseModel

id: UUID
created_at: datetime
updated_at: datetime
version: int
schema_version: str
verified: bool
metadata: dict[str, Any]
```

---

# 5. Domain Models

Domain models represent professional knowledge.

---

## Resume

```python
Resume

id

summary

skills

experience

projects

education

certifications

achievements

metadata
```

---

## ResumeSummary

```python
ResumeSummary

text

keywords

word_count
```

---

## Experience

```python
Experience

id

company

role

location

employment_type

start_date

end_date

technologies

bullets

achievements
```

---

## ExperienceBullet

```python
ExperienceBullet

id

text

metrics

keywords

priority
```

---

## Project

```python
Project

id

title

description

technologies

repository

demo

bullets

category
```

---

## Skill

```python
Skill

id

name

category

years

proficiency

verified
```

---

## Education

```python
Education

id

institution

degree

field

cgpa

start_date

end_date
```

---

## Achievement

```python
Achievement

id

title

description

category

date
```

---

## Certification

```python
Certification

id

name

issuer

credential_id

issue_date
```

---

# 6. Job Description Models

## JobDescription

```python
JobDescription

id

title

company

location

employment_type

description
```

---

## JobRequirements

```python
JobRequirements

required_skills

preferred_skills

responsibilities

soft_skills

keywords

experience_level
```

---

# 7. Workflow Models

These models represent runtime state.

---

## WorkflowState

```python
WorkflowState

request_id

resume

job_description

retrieved_context

rewrite_plan

rewritten_resume

guardrail_report

validation_report

ats_report

telemetry

status
```

Only one workflow state exists for each optimization request.

---

## WorkflowStatus

```python
PENDING

PARSING

INDEXING

RETRIEVING

PLANNING

REWRITING

GUARDRAILS

VALIDATING

RENDERING

COMPLETED

FAILED
```

---

# 8. Retrieval Models

## KnowledgeChunk

```python
KnowledgeChunk

id

content

entity_type

entity_id

metadata

embedding_id

checksum

schema_version
```

---

## ChunkMetadata

```python
ChunkMetadata

source

importance

technologies

category

verified

owner

version

created_at

updated_at
```

---

## RetrievalResult

```python
RetrievalResult

chunk

score

rerank_score

reason
```

---

# 9. Agent Contracts

Agents exchange typed contracts.

---

## PlanningRequest

```python
PlanningRequest

resume

job_requirements

retrieved_chunks
```

---

## RewritePlan

```python
RewritePlan

summary_changes

experience_changes

project_changes

skill_changes

reasoning
```

---

## RewriteRequest

```python
RewriteRequest

resume

rewrite_plan

retrieved_context
```

---

## RewriteResult

```python
RewriteResult

updated_resume

modified_sections

confidence

citations

guardrail_status
```

---

## ATSReport

```python
ATSReport

overall_score

keyword_coverage

missing_keywords

strengths

weaknesses

recommendations
```

---

# 10. Validation Models

## ValidationResult

```python
ValidationResult

passed

errors

warnings

business_rules

hallucination_score

confidence

processing_time
```

---

## ValidationIssue

```python
ValidationIssue

type

severity

message

section

recommendation
```

---

# 11. Guardrail Models

## GuardrailResult

```python
GuardrailResult

passed

repaired

violations

validator_results

processing_time

metadata
```

---

## GuardrailViolation

```python
GuardrailViolation

validator

severity

code

message

location

suggestion
```

---

## PolicyResult

```python
PolicyResult

policy

passed

reason

metadata
```

---

# 12. Rendering Models

## RenderRequest

```python
RenderRequest

resume

template

theme
```

---

## RenderResult

```python
RenderResult

latex

pdf_path

compile_logs
```

---

# 13. API Models

## UploadResumeRequest

```python
file

template_name
```

---

## OptimizeResumeRequest

```python
resume_id

job_description

model

temperature
```

---

## OptimizationResponse

```python
OptimizationResponse

optimization_id

status

estimated_completion

request_id

workflow_id
```

---

## ResumeResponse

```python
ResumeResponse

resume

guardrail_report

validation_report

ats_report

download_url
```

---

# 14. Database Models

## ResumeEntity

```python
id

user_id

version

created_at
```

---

## ResumeVersionEntity

```python
resume_id

version

latex_path

pdf_path
```

---

## OptimizationHistoryEntity

```python
resume_id

job_title

company

ats_score

created_at
```

---

## FeedbackEntity

```python
optimization_id

accepted

comment
```

---

## GuardrailAuditEntity

```python
request_id

validator

status

violations

processing_time

created_at
```

---

## WorkflowEntity

```python
workflow_id

request_id

status

started_at

completed_at
```

---

# 15. Vector Metadata

Each embedded chunk stores metadata.

```json
{
  "entity": "Project",
  "entity_id": "...",
  "category": "AI",
  "importance": 0.96,
  "technologies": ["Python", "LangChain", "FastAPI"],
  "verified": true,
  "version": 3,
  "owner": "resume",
  "schema_version": "1.0"
}
```

---

# 16. Event Models

Tailr follows an event-driven workflow.

Examples

```
ResumeUploaded

ResumeParsed

KnowledgeIndexed

RetrievalCompleted

PlanningCompleted

RewriteCompleted

ValidationCompleted

RenderingCompleted

OptimizationCompleted

GuardrailsStarted

GuardrailsCompleted

GuardrailViolationDetected

ValidationRejected

WorkflowRetried
```

Each event carries structured payloads.

---

# 17. Enumerations

## SkillCategory

```
Frontend

Backend

AI

Cloud

Database

DevOps

Programming Language

Framework

Tool
```

---

## Severity

```
INFO

WARNING

ERROR

CRITICAL
```

---

## EntityType

```
Resume

Experience

Project

Skill

Education

Achievement

Certification
```

---

## ValidationStatus

```
PASSED

FAILED

REPAIRED

SKIPPED
```

---

## GuardrailSeverity

```
LOW

MEDIUM

HIGH

CRITICAL
```

---

# 18. Relationships

```
Resume

│

├── Experience

│      ├── ExperienceBullet

│      └── Technology

│

├── Project

│      ├── Technology

│      └── Repository

├── WorkflowState

│    │

│    ├── GuardrailResult

│    │

│    ├── ValidationResult

│    │

│    └── ATSReport

│

├── Education

├── Skills

├── Certifications

└── Achievements
```

---

# 19. Serialization

All models support:

- JSON serialization
- Pydantic validation
- Database persistence
- Vector metadata generation
- API responses

A single canonical representation prevents data inconsistencies across services.

All serialized models are versioned and validated against their corresponding Pydantic schemas before persistence or inter-service communication.

## This guarantees backward compatibility, deterministic processing, and safe evolution of the platform.

# 20. Versioning Strategy

Every model includes a schema version.

```
Resume

↓

v1

↓

v2

↓

v3
```

Older versions remain readable through migration logic.

---

# 21. Future Models

The model layer is designed to grow without breaking existing contracts.

Planned entities include:

- CoverLetter
- GitHubRepository
- LinkedInProfile
- Application
- Recruiter
- Interview
- Portfolio
- BlogPost
- Publication
- CareerGoal

These entities will integrate with the existing workflow and knowledge graph.

Additional system models may include:

- GuardrailPolicy
- PromptTemplate
- AIModelConfiguration
- EvaluationReport
- ExperimentResult
- TelemetryEvent
- RetryPolicy
- CostMetrics

---

# 22. Summary

The Tailr Data Model establishes a unified contract between every layer of the system.

By separating domain entities, workflow state, agent contracts, API objects, database entities, and vector metadata, Tailr achieves a modular architecture that is deterministic, testable, and extensible.

Every component communicates through strongly typed contracts that are validated, versioned, and protected by deterministic Guardrail policies.

This unified model enables AI agents, workflow orchestration, retrieval, validation, rendering, and observability to operate on a consistent data foundation, ensuring reliability, maintainability, and production-grade scalability.

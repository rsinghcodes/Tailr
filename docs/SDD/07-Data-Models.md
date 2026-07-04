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

# 3. Model Categories

```
                    Data Models
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
 Domain Models     Workflow Models    API Models
      │                  │                  │
      ▼                  ▼                  ▼
Agent Contracts   Database Models   Vector Metadata
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

resume

job_description

retrieved_context

rewrite_plan

rewritten_resume

validation_report

ats_report

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

created_at
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

hallucination_score
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

# 11. Rendering Models

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

# 12. API Models

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
optimization_id

status

estimated_completion
```

---

## ResumeResponse

```python
resume

ats_report

download_url
```

---

# 13. Database Models

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

# 14. Vector Metadata

Each embedded chunk stores metadata.

```json
{
  "entity": "Project",
  "entity_id": "...",
  "category": "AI",
  "importance": 0.96,
  "technologies": ["Python", "LangChain", "FastAPI"]
}
```

---

# 15. Event Models

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
```

Each event carries structured payloads.

---

# 16. Enumerations

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

# 17. Relationships

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

│

├── Education

├── Skills

├── Certifications

└── Achievements
```

---

# 18. Serialization

All models support:

- JSON serialization
- Pydantic validation
- Database persistence
- Vector metadata generation
- API responses

A single canonical representation prevents data inconsistencies across services.

---

# 19. Versioning Strategy

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

# 20. Future Models

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

---

# 21. Summary

The Tailr Data Model establishes a unified contract between every layer of the system.

By separating domain entities, workflow state, agent contracts, API objects, database entities, and vector metadata, Tailr achieves a modular architecture that is deterministic, testable, and extensible.

Every component speaks the same typed language, allowing the platform to evolve without introducing coupling or ambiguity.

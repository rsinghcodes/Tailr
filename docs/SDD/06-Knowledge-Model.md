# Canonical Knowledge Model

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the Canonical Knowledge Model used throughout Tailr.

The Canonical Knowledge Model is the central representation of all user information.

Every component—including parsing, retrieval, planning, validation, rendering, and future AI agents—operates on this model instead of directly manipulating resume documents.

The knowledge model ensures:

- consistency
- explainability
- deterministic behavior
- validation
- long-term extensibility

---

# 2. Why a Knowledge Model?

Traditional resume tools treat resumes as documents.

```
Resume.pdf

↓

LLM

↓

Resume.pdf
```

Tailr instead treats resumes as structured knowledge.

```
Resume.tex

↓

Parser

↓

Canonical Resume Model

↓

Knowledge Graph

↓

RAG

↓

Agents

↓

Renderer
```

The resume becomes an engineering artifact instead of plain text.

---

# 3. Core Principles

## Single Source of Truth

Only one canonical resume exists.

Every optimized resume is derived from it.

---

## Immutable Facts

Facts never change.

Examples

- employer
- dates
- technologies
- projects
- education

AI cannot modify immutable facts.

---

## Mutable Presentation

Presentation may change.

Examples

- summary
- bullet wording
- ordering
- emphasis
- action verbs

---

## Typed Entities

Everything is represented as strongly typed entities.

No free-form JSON blobs.

---

## Relationships

Knowledge is connected through explicit relationships.

Relationships enable reasoning.

---

# 4. High-Level Knowledge Model

```
                     Resume
                        │
      ┌─────────────────┼─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
 Experience          Projects          Education
      │                 │                 │
      ▼                 ▼                 ▼
 Technologies       Skills         Achievements
      │                 │
      └────────────┬────┘
                   ▼
             Knowledge Graph
```

---

# 5. Root Entity

```
Resume
```

Contains

- Summary
- Skills
- Experience
- Projects
- Education
- Achievements
- Certifications

The Resume entity owns all knowledge.

---

# 6. Entity Model

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

## Experience

```python
Experience

company

role

start_date

end_date

location

technologies

bullets

achievements
```

---

## Project

```python
Project

title

description

technologies

bullets

links

category
```

---

## Skill

```python
Skill

name

category

confidence

years

source
```

---

## Education

```python
Education

institution

degree

cgpa

start

end
```

---

## Achievement

```python
Achievement

title

description

date

category
```

---

## Certification

```python
Certification

name

issuer

date

credential
```

---

# 7. Entity Relationships

Relationships are first-class citizens.

```
Experience

↓

USES

↓

Technology
```

```
Project

↓

USES

↓

Technology
```

```
Experience

↓

PRODUCED

↓

Achievement
```

```
Resume

↓

CONTAINS

↓

Experience
```

---

# 8. Knowledge Graph

Example

```
ResearchMind

↓

USES

↓

LangChain

↓

RELATED_TO

↓

Agentic AI

↓

USES

↓

LLMs
```

Another

```
FastAPI

↓

FRAMEWORK_FOR

↓

Python

↓

CATEGORY

↓

Backend
```

Graph traversal enables reasoning beyond embeddings.

---

# 9. Immutable Knowledge

These fields can never change.

```
Company

Role

Dates

Degree

University

Projects

Technologies Actually Used

Certificates

Achievements
```

Validation rejects modifications.

---

# 10. Mutable Knowledge

Allowed modifications

```
Summary

Bullet wording

Section ordering

Action verbs

Project ordering

Skill ordering

Highlighting
```

These are presentation-layer optimizations.

---

# 11. Metadata Model

Every entity stores metadata.

Example

```json
{
  "importance": 0.95,
  "verified": true,
  "embedding": true,
  "source": "resume.tex",
  "created_at": "...",
  "updated_at": "...",
  "version": 3
}
```

Metadata powers retrieval and validation.

---

# 12. Chunk Model

Chunks are created from entities.

```
Project

↓

Chunk
```

```
Experience

↓

Chunk
```

Chunks never split an entity.

Semantic integrity is preserved.

---

# 13. Embedding Model

Every chunk produces

```
Chunk

↓

Embedding

↓

Vector

↓

Qdrant
```

Embeddings never replace structured entities.

Vectors are indexes, not truth.

---

# 14. Knowledge Layers

Tailr separates knowledge into layers.

```
Presentation Layer

↓

Canonical Model

↓

Knowledge Graph

↓

Vector Index

↓

Retriever

↓

Agents
```

Every layer has one responsibility.

---

# 15. Resume Versioning

```
Resume v1

↓

Resume v2

↓

Resume v3

↓

Resume v4
```

Each version references the same canonical facts.

Only presentation changes.

---

# 16. Knowledge Evolution

The model grows over time.

New entities

- Interview
- Recruiter
- Company
- Application
- Portfolio
- GitHub Repository
- Blog
- Research Paper

The architecture supports expansion without redesign.

---

# 17. Query Examples

```
Show AI projects
```

↓

Retrieve

```
Project

category=AI
```

---

```
Show backend experience
```

↓

Traverse

```
Experience

↓

Technology

↓

Backend
```

---

```
Show LangChain work
```

↓

Search

```
Project

↓

Technology

↓

LangChain
```

---

# 18. Validation Rules

Every entity validates itself.

Example

Experience

Required

- company
- role
- start_date
- bullets

Project

Required

- title
- technologies

Validation prevents incomplete knowledge.

---

# 19. Serialization

The Canonical Model is serialized as JSON.

Example

```
Resume

↓

JSON

↓

Database

↓

Retriever

↓

Renderer
```

This enables deterministic workflows.

---

# 20. Knowledge Lifecycle

```
Resume.tex

↓

Parser

↓

Canonical Model

↓

Knowledge Graph

↓

Vector Index

↓

Retriever

↓

Planner

↓

Rewrite

↓

Validator

↓

Renderer

↓

Resume.tex
```

Knowledge is preserved throughout the pipeline.

---

# 21. Future Extensions

Future entities

- GitHub Repository
- Stack Overflow
- LinkedIn
- Research Paper
- Hackathon
- Open Source Contribution
- Publications
- Certifications
- Recruiter Feedback
- Interview Performance

These integrate into the same graph.

---

# 22. Summary

The Canonical Knowledge Model is the foundation of Tailr.

Instead of treating resumes as editable documents, Tailr models professional history as structured knowledge composed of typed entities and explicit relationships.

This model enables:

- deterministic validation
- semantic retrieval
- explainable AI
- graph reasoning
- long-term memory
- reusable workflows

Every AI agent, retrieval pipeline, validator, and renderer operates on this model, making it the single source of truth for the entire platform.

# System Architecture

**Project:** Tailr

**Document Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document describes the overall system architecture of Tailr.

It defines the major components, their responsibilities, communication patterns, data flow, deployment model, and architectural decisions.

This document intentionally focuses on system-level design. Component-level implementation details are described in subsequent documents.

---

# 2. Architecture Principles

Tailr follows six architectural principles.

## 2.1 Single Source of Truth

The master resume is the canonical representation of the user's professional history.

Every optimized resume is derived from this source.

No AI component may introduce information that does not exist in the canonical resume model.

---

## 2.2 Retrieval Before Generation

Large Language Models should never receive the complete resume.

Instead,

Relevant information is retrieved first.

Generation occurs only after retrieval.

---

## 2.3 Deterministic Rendering

LLMs never generate LaTeX.

The renderer is responsible for producing compilable documents.

---

## 2.4 Explainability

Every AI-generated modification must include:

- reasoning
- evidence
- confidence
- affected resume section

---

## 2.5 Modular Components

Each component has exactly one responsibility.

Components communicate using typed schemas.

---

## 2.6 Local-First AI

The architecture supports fully offline execution.

Cloud LLMs remain optional.

---

# 3. High-Level Architecture

```

```

                           User
                             │
                             ▼
                    Next.js Frontend
                             │
                             ▼
                       FastAPI Backend
                             │
                             ▼
                  LlamaIndex Workflow Engine
                             │
      ┌──────────────────────┼───────────────────────┐
      │                      │                       │
      ▼                      ▼                       ▼

Resume Parser JD Analyzer Knowledge Engine
│ │ │
└──────────────┬───────┴──────────────┬────────┘
▼ ▼
Canonical Resume Qdrant Vector DB
│ │
└──────────┬───────────┘
▼
Hybrid Retriever
│
▼
Planning Agent
│
▼
Rewrite Agent
│
▼
Validation Engine
│
▼
ATS Analyzer
│
▼
LaTeX Rendering Engine
│
▼
latexmk Compiler
│
▼
PDF + Reports + Diff

```

---

# 4. Logical Layers

Tailr is organized into multiple architectural layers.

```

Presentation Layer

↓

Application Layer

↓

Workflow Layer

↓

Knowledge Layer

↓

AI Layer

↓

Validation Layer

↓

Rendering Layer

↓

Infrastructure Layer

```

---

# 5. Layer Responsibilities

## Presentation Layer

Responsibilities

- Resume upload
- JD upload
- Progress tracking
- Diff viewer
- ATS dashboard
- Resume preview

Technology

- Next.js
- TailwindCSS

---

## API Layer

Responsibilities

- Authentication
- Request validation
- Upload handling
- Streaming responses
- File management

Technology

- FastAPI

---

## Workflow Layer

Coordinates the complete optimization process.

Responsibilities

- State management
- Retry handling
- Routing
- Agent orchestration

Technology

- LlamaIndex Workflows

---

## Knowledge Layer

Responsible for creating structured knowledge.

Responsibilities

- Resume indexing
- JD indexing
- Career guide indexing
- Metadata filtering
- Retrieval

Technology

- LlamaIndex

---

## AI Layer

Responsible only for reasoning.

Contains

- Planner
- Rewriter
- ATS explanation

LLMs never manipulate raw files.

---

## Validation Layer

Responsible for enforcing correctness.

Contains

- Rule engine
- Schema validation
- Hallucination detection
- Confidence scoring

---

## Rendering Layer

Responsible for deterministic output.

Converts

Resume Model

↓

LaTeX

↓

PDF

---

## Infrastructure Layer

Provides persistent storage.

Contains

- PostgreSQL
- Qdrant
- Redis
- Ollama

---

# 6. Core Components

## Resume Parser

Purpose

Convert LaTeX into structured data.

Input

resume.tex

Output

Canonical Resume Model

---

## JD Analyzer

Purpose

Extract structured information from job descriptions.

Input

Job Description

Output

Job Requirement Model

---

## Knowledge Engine

Purpose

Convert structured information into searchable knowledge.

Responsibilities

- Chunking
- Embeddings
- Metadata
- Indexing

---

## Hybrid Retriever

Purpose

Retrieve only relevant context.

Pipeline

Dense Search

↓

Sparse Search

↓

Merge

↓

Reranker

↓

Top-K

---

## Planner Agent

Purpose

Generate an optimization strategy.

Example

```

Summary

↓

Mention Agentic AI

Projects

↓

Move ResearchMind first

Skills

↓

Promote FastAPI

```

---

## Rewrite Agent

Purpose

Rewrite only approved sections.

Cannot

- invent projects
- invent employers
- invent metrics

---

## Validation Engine

Responsible for verifying

- factual correctness
- schema
- formatting
- unsupported claims

---

## ATS Engine

Responsible for

- keyword coverage
- semantic similarity
- readability
- action verbs
- quantified impact

---

## Rendering Engine

Responsible for deterministic LaTeX generation.

LLMs never generate LaTeX.

---

# 7. Data Flow

```

Resume.tex

↓

Parser

↓

Resume Model

↓

Knowledge Index

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

latexmk

↓

PDF

```

---

# 8. Knowledge Architecture

Tailr maintains multiple indexes.

```

Qdrant

├── resume_index

├── jd_index

├── skills_index

├── project_index

├── guides_index

├── resume_versions

└── feedback_index

```

Each collection serves a distinct purpose.

---

# 9. Resume Lifecycle

```

Upload

↓

Parse

↓

Normalize

↓

Index

↓

Optimize

↓

Validate

↓

Render

↓

Compile

↓

Store

↓

Download

```

---

# 10. Request Lifecycle

```

HTTP Request

↓

Authentication

↓

Validation

↓

Workflow

↓

Retriever

↓

Planner

↓

Rewrite

↓

Validation

↓

Rendering

↓

Response

```

---

# 11. Deployment Architecture

```

Docker Compose

├── frontend

├── backend

├── postgres

├── qdrant

├── redis

├── ollama

└── langfuse

```

Production

```

Internet

↓

NGINX

↓

Frontend

↓

Backend

↓

Workflow

↓

Qdrant

↓

PostgreSQL

↓

Redis

↓

Ollama

```

---

# 12. Technology Stack

| Layer | Technology |
|---------|------------|
| Frontend | Next.js |
| Backend | FastAPI |
| Workflow | LlamaIndex Workflows |
| RAG | LlamaIndex |
| Vector DB | Qdrant |
| Database | PostgreSQL |
| Cache | Redis |
| Embeddings | BAAI BGE Small |
| Reranker | BAAI BGE Reranker |
| LLM | Ollama + Qwen3 |
| Observability | Langfuse |
| Evaluation | Ragas |
| PDF | latexmk |
| Containers | Docker Compose |

---

# 13. Scalability

The architecture supports independent scaling of:

- API servers
- Workflow workers
- Vector database
- LLM inference
- Rendering service

This enables future cloud deployment without architectural changes.

---

# 14. Fault Tolerance

Each workflow step is isolated.

If one component fails,

```

Retry

↓

Fallback

↓

Human Review

↓

Abort

```

Examples

Parser Failure

↓

Stop Workflow

LLM Failure

↓

Retry

Validation Failure

↓

Reject Rewrite

Compilation Failure

↓

Return Logs

---

# 15. Security Architecture

Security boundaries exist between

- User uploads
- LLM execution
- Knowledge storage
- Rendering
- PDF compilation

Every uploaded file is validated before processing.

LaTeX compilation occurs in an isolated environment.

---

# 16. Architecture Decision Summary

| Decision | Reason |
|-----------|--------|
| Canonical Resume Model | Single source of truth |
| LlamaIndex | Native RAG & workflows |
| Qdrant | Open-source vector search |
| Ollama | Local inference |
| Hybrid Retrieval | Higher retrieval accuracy |
| Rule-Based Validation | Prevent hallucinations |
| Renderer Generates LaTeX | Deterministic output |

---

# 17. Future Evolution

The current architecture is designed to evolve into a complete Career Intelligence Platform.

Future modules may include:

- Cover Letter Generator
- LinkedIn Optimizer
- GitHub Analyzer
- Portfolio Analyzer
- Interview Coach
- Career Knowledge Graph
- Application Tracker
- Recruiter CRM
- Analytics Dashboard

These modules can reuse the existing knowledge, workflow, and validation layers without requiring architectural redesign.

---

# 18. Summary

Tailr adopts a layered, modular, and knowledge-centric architecture that separates reasoning from validation and rendering.

The architecture prioritizes:

- correctness over creativity
- explainability over opacity
- modularity over monolithic design
- retrieval over large prompts
- deterministic rendering over AI-generated formatting

This foundation enables Tailr to evolve from a resume optimizer into a comprehensive AI-powered Career Intelligence Platform.
```

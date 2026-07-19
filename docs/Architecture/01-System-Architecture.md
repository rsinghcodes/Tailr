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

## Guardrails Layer

The Guardrails Layer sits between the AI Layer and the Validation Layer.

Its responsibility is to ensure that every interaction with an LLM is safe, deterministic, and compliant with system policies before business validation occurs.

Responsibilities

- Validate LLM inputs
- Validate LLM outputs
- Enforce structured JSON schemas
- Detect prompt injection attempts
- Detect prompt leakage
- Detect hallucinated content
- Detect Personally Identifiable Information (PII) leakage
- Enforce resume integrity policies
- Enforce ATS formatting constraints
- Repair recoverable outputs when possible

The Guardrails Layer is provider-independent and is executed for every AI workflow regardless of the underlying model (Ollama, OpenAI, Anthropic, etc.).

Typical execution flow

```

AI Layer

↓

Guardrails

↓

Validation Layer

↓

Rendering Layer

```

The Guardrails Layer never performs business decisions.

It only ensures that generated content is safe and structurally correct before validation rules are applied.

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

Responsible for verifying business correctness after Guardrails have approved the AI output.

Checks include

- factual correctness
- resume integrity
- schema compliance
- formatting rules
- unsupported claims
- ATS compliance
- business policies

Unlike the Guardrails Layer, the Validation Engine focuses on business correctness rather than AI safety.

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

Guardrails

↓

Validation

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

Guardrails

↓

Validate

↓

Render

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

Request Validation

↓

Workflow

↓

Retriever

↓

Planner

↓

Rewrite

↓

Guardrails

↓

Business Validation

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

### Guardrail Failures

If Guardrails reject AI output, the workflow follows one of the following recovery strategies:

1. Retry with a stricter prompt.
2. Retry using a fallback model.
3. Attempt automatic output repair.
4. Escalate for manual review.
5. Abort the workflow if safety cannot be guaranteed.

Guardrail failures are logged for observability and future model evaluation.

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

Additional security measures include:

- Prompt Injection Detection
- Prompt Leakage Detection
- Structured Output Validation
- Resume Integrity Enforcement
- Output Sanitization
- PII Protection
- AI Safety Policies

Every AI response passes through the Guardrails Layer before entering the Validation Layer.

---

# 16. Architecture Decision Summary

| Decision | Reason |
|-----------|--------|
| Canonical Resume Model | Single source of truth |
| LlamaIndex | Native RAG & workflows |
| Qdrant | Open-source vector search |
| Ollama | Local inference |
| Hybrid Retrieval | Higher retrieval accuracy |
| Guardrails Layer | Enforce AI safety, schema validation, and prompt security |
| Rule-Based Validation | Enforce business correctness and resume integrity |
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

# 18. AI Safety & Guardrails

Every AI-generated response follows a standardized Guardrails Pipeline before business validation.

Pipeline

```

LLM Output

↓

JSON Validation

↓

Schema Validation

↓

Prompt Injection Detection

↓

Hallucination Detection

↓

Resume Integrity Validation

↓

ATS Formatting Validation

↓

PII Detection

↓

Business Validation

↓

Rendering

```

This architecture ensures that AI outputs remain trustworthy, explainable, and production-ready regardless of the underlying LLM provider.

# 19. Summary

Tailr adopts a layered, modular, and knowledge-centric architecture that separates reasoning, AI safety, business validation, and deterministic rendering into independent architectural layers. This separation improves maintainability, observability, and the reliability of AI-generated outputs.

The architecture prioritizes:

- correctness over creativity
- explainability over opacity
- modularity over monolithic design
- retrieval over large prompts
- deterministic rendering over AI-generated formatting

This foundation enables Tailr to evolve from a resume optimizer into a comprehensive AI-powered Career Intelligence Platform.
```

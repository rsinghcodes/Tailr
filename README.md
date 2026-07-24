<div align="center">

# 🚀 Tailr

### AI-Powered Resume Intelligence Platform

**Optimize your resume for every job description using Multi-Agent AI, RAG, and LLMs — while preserving truth, enforcing AI safety, and producing ATS-compatible LaTeX output.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)]()
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=nextdotjs)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)]()
[![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)]()

---

### ✨ Build one master resume. Tailor it infinitely.

</div>

---

# 📖 Overview

**Tailr** is an AI-powered resume optimization platform that automatically tailors a master resume for a specific job description while preserving factual accuracy.

Unlike traditional resume generators, Tailr **never fabricates experience**. Every optimization is grounded in the user's existing resume, validated through a mandatory Guardrails Engine, and rendered deterministically.

Instead of editing LaTeX directly, Tailr converts the resume into a structured knowledge model, retrieves relevant context via RAG, applies AI-powered transformations through a multi-agent pipeline, validates every modification through guardrails, and renders a compilable LaTeX resume.

---

# ✨ Features

## Core

- 🤖 Multi-Agent AI workflow orchestrated by LangGraph
- 📄 Native LaTeX (Overleaf) resume support
- 🎯 ATS optimization & scoring
- 🧠 RAG-powered contextual rewriting via LlamaIndex
- 🔍 Hybrid retrieval (dense + sparse + reranking)
- 📊 Resume gap analysis
- 📈 Explainable AI recommendations with evidence citations
- 📝 Resume diff viewer & version control
- 📑 Deterministic PDF generation via latexmk

## AI Safety & Guardrails

- 🛡 Mandatory Guardrails Engine on every AI output
- 🚫 Hallucination detection against the Canonical Resume Model
- 🔒 Prompt injection detection & prevention
- 🔐 PII / secret scanning
- ✅ Structured output validation (JSON + schema)
- 🔧 Automatic output repair for recoverable issues
- 📋 Resume integrity validation (no invented employers, projects, metrics, or dates)
- 🧪 ATS formatting validation
- 🔰 LaTeX safety validation (no shell escape, no unsafe commands)

## Platform

- ⚡ Async FastAPI backend
- 🎨 Next.js frontend with TypeScript
- 🐳 Dockerized development
- 📚 OpenAPI documentation
- 🔭 OpenTelemetry observability
- 📊 Langfuse tracing
- 🏠 Local-first AI (Ollama) — cloud LLMs optional

---

# 🏗 Architecture

```text
                    Resume.tex
                         │
                         ▼
                Resume Parsing Engine
                         │
                         ▼
              Canonical Resume Model
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      Resume Knowledge         Job Description
             │                       │
             └───────────┬───────────┘
                         ▼
              LlamaIndex RAG Pipeline
           (Hybrid Retrieval + Reranking)
                         │
                         ▼
              LangGraph Workflow Engine
                         │
      ┌──────────┬───────┴──────┬──────────┐
      ▼          ▼              ▼          ▼
 JD Analyzer  Planner      Rewriter  Optimizer
      │          │              │          │
      └──────────┴──────────────┴──────────┘
                         │
                         ▼
               Guardrails Engine
          (Hallucination · Injection ·
           Schema · PII · ATS · LaTeX)
                         │
                         ▼
              Validation Engine
                         │
                         ▼
                  ATS Evaluation
                         │
                         ▼
               Resume Renderer
                         │
                         ▼
                PDF + LaTeX Output
```

---

# 🎯 Design Principles

Tailr follows six architectural principles:

1. **Single Source of Truth** — The master resume is the canonical representation. No AI may introduce information that doesn't exist in it.
2. **Retrieval Before Generation** — LLMs never receive the complete resume. Relevant context is retrieved first via RAG.
3. **Deterministic Rendering** — LLMs never generate LaTeX. The renderer produces compilable documents deterministically.
4. **Explainability** — Every AI modification includes reasoning, evidence, confidence, and the affected section.
5. **Modular Components** — Each component has exactly one responsibility and communicates using typed schemas.
6. **Local-First AI** — The architecture supports fully offline execution. Cloud LLMs are optional.

---

# 🧠 AI Pipeline

```text
Resume.tex
      │
      ▼
Parser → Canonical Resume Model
      │
      ▼
Knowledge Indexing (LlamaIndex → Qdrant)
      │
      ▼
JD Analyzer Agent
      │
      ▼
Resume Analyzer Agent
      │
      ▼
Hybrid Retrieval (Dense + BM25 + Reranker)
      │
      ▼
Guardrails — Prompt Injection Scan (on retrieved context)
      │
      ▼
Planning Agent
      │
      ▼
Rewrite Agent → LLM
      │
      ▼
Guardrails Engine (Schema · Hallucination · Integrity · PII · ATS · LaTeX)
      │
      ▼
Validation Engine (Business Rules)
      │
      ▼
ATS Scoring
      │
      ▼
Human Approval
      │
      ▼
LaTeX Renderer → latexmk → PDF
```

---

# 🛠 Tech Stack

## Frontend

- Next.js (App Router)
- React
- TypeScript (strict mode)
- Tailwind CSS
- TanStack Query
- Zustand
- ShadCN UI
- React Hook Form
- Zod

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.x (Async)
- Alembic
- Pydantic v2
- HTTPX

## AI & RAG

- **LlamaIndex** — RAG, indexing, retrieval, embedding, context assembly
- **LangGraph** — Workflow orchestration, multi-agent coordination, state machines
- Ollama (local inference)
- Qwen3 (default model)
- HuggingFace Embeddings (BAAI/bge-small-en-v1.5)

## Data & Storage

- PostgreSQL 18
- Qdrant Cloud (vector search)
- Redis (caching)

## Observability

- OpenTelemetry
- Langfuse
- Prometheus
- Structured JSON logging

## Evaluation

- RAGAS

## Infrastructure

- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Ruff (linting)
- MyPy (type checking)
- Pytest (testing)
- latexmk (PDF compilation)

---

# 🤖 AI Agents

| Agent             | Responsibility                                                        |
| ----------------- | --------------------------------------------------------------------- |
| JD Analyzer       | Extract structured requirements from job descriptions                 |
| Resume Analyzer   | Analyze strengths, weaknesses, and missing keywords                   |
| Planner           | Create an evidence-backed optimization strategy                       |
| Retriever         | Retrieve relevant context via hybrid search (LlamaIndex + Qdrant)     |
| Rewriter          | Rewrite resume sections using only retrieved evidence                 |
| Guardrails Engine | Validate every AI output for safety, integrity, and schema compliance |
| Validator         | Verify business correctness after guardrails approval                 |
| ATS Scorer        | Evaluate ATS compatibility and generate recommendations               |
| Critic            | Identify weaknesses in the rewritten draft                            |
| Optimizer         | Improve the draft (output re-validated through Guardrails)            |

All agents communicate via **typed JSON events**. Agents never call each other directly — **LangGraph** orchestrates execution.

---

# 📈 Roadmap

### Phase 1 — Foundation (MVP)

- LaTeX resume parser
- Canonical Resume Model
- Knowledge indexing (LlamaIndex + Qdrant)
- Multi-agent workflow (LangGraph)
- Resume rewriting with RAG
- Guardrails Engine (hallucination, injection, PII, ATS, LaTeX safety)
- Validation Engine
- ATS scoring
- PDF generation
- Resume versioning
- Basic dashboard

### Phase 2 — Intelligence

- Cover letter generator
- LinkedIn profile optimizer
- GitHub repository analyzer
- Skill gap analysis
- Multi-resume management
- Guardrail analytics dashboard

### Phase 3 — Career Copilot

- Interview preparation agent
- Mock interview feedback
- Application tracker
- Personalized learning roadmaps
- Salary benchmarking

### Phase 4 — Career Intelligence Platform

- Career timeline & knowledge graph
- Industry trends & hiring intelligence
- Career health score
- AI governance center

### Phase 5 — Enterprise

- Multi-tenant architecture
- Recruiter dashboard
- University placement portal
- API platform
- White-label deployment

---

# 🚀 Getting Started

## Clone

```bash
git clone https://github.com/rsinghcodes/tailr.git

cd tailr
```

---

## Backend

```bash
cd apps/backend

python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Frontend

```bash
cd apps/frontend

npm install

npm run dev
```

---

## Start Infrastructure

```bash
docker compose up -d
```

This starts:

- Redis
- Ollama

> **Note:** PostgreSQL and Qdrant are configured separately. See the deployment docs for full setup.

---

# 📊 Development Status

| Module                          | Status         |
| ------------------------------- | -------------- |
| Backend Foundation              | 🚧 In Progress |
| Resume Parser                   | ⏳ Planned     |
| Canonical Resume Model          | ⏳ Planned     |
| Knowledge Indexing (LlamaIndex) | ⏳ Planned     |
| RAG Pipeline                    | ⏳ Planned     |
| AI Agents                       | ⏳ Planned     |
| Workflow Engine (LangGraph)     | ⏳ Planned     |
| Guardrails Engine               | ⏳ Planned     |
| Validation Engine               | ⏳ Planned     |
| ATS Engine                      | ⏳ Planned     |
| LaTeX Renderer                  | ⏳ Planned     |
| Frontend Dashboard              | ⏳ Planned     |

---

# 🎯 Why Tailr?

Most resume tools simply ask an LLM to rewrite your resume.

Tailr takes a different approach:

- **Parse** → Convert LaTeX into a structured knowledge model
- **Index** → Build searchable resume knowledge via LlamaIndex + Qdrant
- **Retrieve** → Use hybrid RAG for evidence-based context
- **Plan** → Think before rewriting with a dedicated planning agent
- **Rewrite** → Optimize sections using only retrieved evidence
- **Guard** → Validate every AI output through mandatory guardrails
- **Validate** → Enforce business rules and resume integrity
- **Score** → Evaluate ATS compatibility with detailed reports
- **Render** → Generate deterministic, compilable LaTeX

The result is a resume optimization system that is **accurate, explainable, safe, and production-ready**.

---

# 📚 Documentation

Detailed engineering documentation is available in the [`docs/`](docs/) directory:

- [Vision & Mission](docs/Vision.md)
- [Requirements](docs/Requirements.md)
- [Product Roadmap](docs/Roadmap.md)
- [System Architecture](docs/Architecture/01-System-Architecture.md)
- [Agent Architecture](docs/Architecture/02-Agent-Architecture.md)
- [RAG Architecture](docs/Architecture/03-Knowledge-RAG-Architecture.md)
- [Workflow Design](docs/Architecture/06-Workflow-Design.md)
- [Deployment Architecture](docs/Architecture/14-Deployment.md)

Architecture Decision Records (ADRs) are in [`docs/ADR/`](docs/ADR/).

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve Tailr, feel free to open an issue or submit a pull request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

# 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Built using FastAPI, Next.js, LlamaIndex, LangGraph, Qdrant, Ollama, and modern AI engineering practices.**

⭐ Star this repository if you find it useful!

</div>

<div align="center">

# 🚀 Tailr

### AI-Powered Resume Tailoring Platform

**Optimize your resume for every job description using Multi-Agent AI, RAG, and LLMs — while preserving truth, ATS compatibility, and LaTeX formatting.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)]()
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=nextdotjs)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)]()
[![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)]()

---

### ✨ Build one master resume. Tailor it infinitely.

</div>

---

# 📖 Overview

**Tailr** is an AI-powered resume optimization platform that automatically tailors a master resume for a specific job description while preserving factual accuracy.

Unlike traditional resume generators, Tailr **never fabricates experience**. Every optimization is grounded in the user's existing resume and validated before generation.

Instead of editing LaTeX directly, Tailr converts the resume into a structured knowledge model, applies AI-powered transformations, validates every modification, and finally renders a compilable LaTeX resume.

---

# ✨ Features

- 🤖 Multi-Agent AI workflow
- 📄 Native LaTeX (Overleaf) resume support
- 🎯 ATS optimization & scoring
- 🧠 RAG-powered contextual rewriting
- 🔍 Semantic keyword matching
- 📊 Resume gap analysis
- 📈 Explainable AI recommendations
- 📝 Resume diff viewer
- 🛡 Hallucination prevention
- 📑 PDF generation
- ⚡ FastAPI backend
- 🎨 Next.js frontend
- 🐳 Dockerized development
- 📚 OpenAPI documentation

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
                 RAG Retrieval Engine
                         │
                         ▼
                 Multi-Agent Pipeline
                         │
      ┌──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼
 JD Analyzer  Planner   Rewriter  Validator
      │          │          │          │
      └──────────┴──────────┴──────────┘
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

Tailr follows five engineering principles:

- The master resume is the single source of truth.
- AI suggests changes; deterministic code validates them.
- Never fabricate skills, projects, companies, or achievements.
- LLMs never modify raw LaTeX directly.
- Every modification must be explainable and reversible.

---

# 🧠 AI Pipeline

```text
Resume.tex
      │
      ▼
Parser
      │
      ▼
Structured Resume
      │
      ▼
JD Analyzer
      │
      ▼
Gap Analysis
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
ATS Scoring
      │
      ▼
Resume Renderer
      │
      ▼
Optimized Resume.tex
```

---

# 🛠 Tech Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- React Query
- Zustand

## Backend

- FastAPI
- Python 3.12+
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- PostgreSQL
- Redis

## AI Stack

- Ollama
- Qwen3
- LlamaIndex
- HuggingFace Embeddings
- Qdrant Cloud
- RAG

## Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- Ruff
- MyPy
- Pytest

---

# 🤖 AI Agents

| Agent           | Responsibility                                |
| --------------- | --------------------------------------------- |
| JD Analyzer     | Extract requirements from the job description |
| Resume Analyzer | Analyze the current resume                    |
| Planner         | Create an optimization plan                   |
| Retriever       | Retrieve relevant resume context using RAG    |
| Rewriter        | Rewrite resume sections                       |
| Validator       | Prevent hallucinations                        |
| ATS Scorer      | Evaluate ATS compatibility                    |

---

# 📈 Roadmap

### Phase 1 — MVP

- Resume parser
- JD analyzer
- Resume rewriting
- PDF generation

### Phase 2

- Multi-agent orchestration
- Validation engine
- ATS scoring
- Semantic retrieval

### Phase 3

- Multiple resume templates
- Cover letter generation
- Batch optimization
- Recruiter outreach

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
cd backend

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
cd frontend

npm install

npm run dev
```

---

## Start Infrastructure

```bash
docker compose up -d
```

This starts

- PostgreSQL
- Redis
- Ollama

---

# 📊 Development Status

| Module             | Status         |
| ------------------ | -------------- |
| Backend Foundation | 🚧 In Progress |
| Resume Parser      | ⏳ Planned     |
| Knowledge Model    | ⏳ Planned     |
| RAG Engine         | ⏳ Planned     |
| AI Agents          | ⏳ Planned     |
| Workflow Engine    | ⏳ Planned     |
| ATS Engine         | ⏳ Planned     |
| Frontend Dashboard | ⏳ Planned     |

---

# 🎯 Why Tailr?

Most resume tools simply ask an LLM to rewrite your resume.

Tailr takes a different approach.

- Parse → Don't prompt raw LaTeX
- Plan → Think before rewriting
- Retrieve → Use RAG for context
- Validate → Prevent hallucinations
- Render → Generate deterministic LaTeX

The result is a resume optimization system that is **accurate, explainable, and production-ready**.

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve Tailr, feel free to open an issue or submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Built using FastAPI, Next.js, LlamaIndex, Qdrant, Ollama, and modern AI engineering practices.**

⭐ Star this repository if you find it useful!

</div>

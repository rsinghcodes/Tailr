<div align="center">

# Tailr

### AI-Powered Resume Intelligence Platform

**Upload a resume, paste a job description — get an AI-optimized version grounded in your real experience.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)]()
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=nextdotjs)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql)]()
[![Gemini](https://img.shields.io/badge/Gemini_3.6_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)]()
[![Qdrant](https://img.shields.io/badge/Qdrant_Cloud-3A3A3A?style=for-the-badge&logo=qdrant&logoColor=white)]()

</div>

# Overview

Tailr is an AI-powered resume optimization platform. Unlike traditional resume generators, Tailr **never fabricates experience** — every optimization is grounded in the user's existing resume via RAG (Retrieval-Augmented Generation).

**Core flow:**

1. Upload a resume (PDF/DOCX/TXT) → LlamaExtract extracts structured JSON
2. Paste a job description → LlamaExtract extracts structured requirements
3. Section-by-section embeddings → semantic search in Qdrant Cloud
4. Retrieve context → LLM optimizes each section
5. Display the optimized result

# Architecture

```mermaid
flowchart TD
    A["Resume File<br/>(PDF / DOCX / TXT)"] --> B["LlamaExtract<br/>(Structured JSON)"]

    B --> C["Section Embeddings<br/>(Qdrant Cloud)"]
    B --> D["Job Description<br/>(LlamaExtract)"]

    C --> E["Semantic Retrieval"]
    D --> E

    E --> F["Gemini 3.6 Flash LLM<br/>(LangGraph Workflow)"]
    F --> G["Optimized Resume Output"]
```

# Features

- **AI-Powered Extraction** — LlamaExtract converts PDF/DOCX/TXT into structured JSON (experience, education, skills, projects, certifications, achievements)
- **Section-by-Section Embeddings** — Each section (summary, skills, experience, etc.) is independently embedded for precise retrieval
- **Semantic RAG** — Qdrant Cloud vector search retrieves the most relevant sections for the target job
- **Multi-Agent Workflow** — LangGraph orchestrates JD analysis, resume analysis, planning, rewriting, and optimization
- **Streaming Results** — Frontend receives real-time SSE events as the workflow progresses
- **Data Management** — View, use, or delete previously extracted resumes and job descriptions
- **JWT Authentication** — Secure user accounts with bcrypt password hashing
- **Clean Architecture** — Domain-driven design with repository pattern and dependency injection

# Tech Stack

## Frontend

- **Next.js 16** (App Router)
- **React 19**
- **TypeScript** (strict mode)
- **Tailwind CSS v4**
- **React Query v5**
- **Zustand**
- **ShadCN UI**

## Backend

- **Python 3.13**
- **FastAPI**
- **SQLAlchemy 2.x** (async)
- **Alembic**
- **Pydantic v2**
- **LangChain**
- **LangGraph**

## AI & Vector

- **Google Gemini 3.6 Flash** (LLM)
- **Google Gemini Embeddings** (`models/gemini-embedding-001`, 3072 dims)
- **LlamaExtract** (structured data extraction from files)
- **Qdrant Cloud** (vector database)

## Storage

- **PostgreSQL 17** (relational data)
- **Qdrant Cloud** (vector embeddings)
- **Redis** (caching — optional)

# Getting Started

## Prerequisites

- Python 3.13+
- Node.js 22+
- PostgreSQL 17
- Qdrant Cloud account
- Google Gemini API key
- LlamaExtract API key

## Backend

```powershell
cd apps/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in `apps/backend`:

```ini
DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/tailr
GEMINI_API_KEY=your_key_here
LLAMAEXTRACT_API_TOKEN=your_token_here
QDRANT_URL=https://your-instance.eu-west-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=your_key_here
JWT_SECRET_KEY=your_secret
```

Run migrations:

```powershell
alembic upgrade head
```

Start the server:

```powershell
uvicorn api.main:app --reload
```

## Frontend

```powershell
cd apps/frontend
npm install
npm run dev
```

# Project Structure

```
apps/
├── backend/
│   ├── api/
│   │   ├── routes/          # FastAPI route handlers
│   │   └── main.py          # App entrypoint
│   ├── application/         # Use cases / service layer
│   ├── domain/              # Business entities & repository interfaces
│   ├── infrastructure/
│   │   ├── database/        # SQLAlchemy models & session
│   │   ├── llamaindex/      # LlamaExtract + Qdrant vector store
│   │   └── repositories/    # SQLAlchemy repository implementations
│   ├── workflows/           # LangGraph workflow nodes & graph
│   └── alembic/             # Database migrations
└── frontend/
    ├── app/                 # Next.js App Router pages
    ├── components/          # React components
    └── lib/                 # Zustand stores & utilities
```

# Development Status

| Module                  | Status      |
| ----------------------- | ----------- |
| User Auth (JWT)         | ✅ Complete |
| Resume Upload & Extract | ✅ Complete |
| JD Upload & Extract     | ✅ Complete |
| Qdrant Indexing         | ✅ Complete |
| Semantic Retrieval      | ✅ Complete |
| LangGraph Workflow      | ✅ Complete |
| SSE Streaming           | ✅ Complete |
| Data Management         | ✅ Complete |
| Guardrails              | ⏳ Planned  |
| ATS Scoring             | ⏳ Planned  |
| PDF Generation          | ⏳ Planned  |

# License

MIT

<div align="center">

**Built with FastAPI, Next.js, LangGraph, Gemini, Qdrant Cloud, and LlamaExtract.**

</div>

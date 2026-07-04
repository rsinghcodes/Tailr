# Knowledge & RAG Architecture

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document describes the Knowledge Architecture of Tailr.

Unlike conventional Retrieval-Augmented Generation (RAG) systems that index documents and retrieve similar chunks, Tailr builds multiple domain-specific knowledge bases that collectively represent the user's professional history and career context.

The objective is to ensure every AI decision is grounded in retrieved evidence rather than relying solely on the LLM's internal knowledge.

---

# 2. Why RAG?

A naive resume optimization system sends the entire resume and job description to an LLM.

```
Resume

+

Job Description

↓

LLM

↓

Resume
```

Problems

- Large prompts
- High token cost
- Poor scalability
- Weak reasoning
- Context window limitations
- Hallucinations

Tailr instead retrieves only the information required for the current reasoning task.

```
Resume

↓

Knowledge Index

↓

Retriever

↓

Relevant Context

↓

LLM
```

---

# 3. Design Principles

Tailr follows six knowledge principles.

## Knowledge Before Generation

Every reasoning step begins with retrieval.

---

## Multiple Specialized Knowledge Bases

Knowledge is separated by purpose.

Resume knowledge is different from career guides.

Job descriptions are different from projects.

---

## Immutable Knowledge

The canonical resume never changes.

Generated resumes are derived artifacts.

---

## Structured Metadata

Every chunk contains rich metadata.

Example

```
type = project

technology = FastAPI

role = Backend

company = ATC

experience = 3 years
```

---

## Retrieval Is Explainable

Every retrieved chunk is traceable.

The system records

- why it was retrieved
- similarity score
- metadata
- consuming agent

---

## Local First

The knowledge layer operates entirely on local infrastructure.

No external vector services are required.

---

# 4. Knowledge Architecture

```
                     Canonical Resume
                             │
                             ▼
                    Knowledge Builder
                             │
        ┌────────────────────┼─────────────────────┐
        │                    │                     │
        ▼                    ▼                     ▼
 Resume Knowledge      Skills Knowledge     Project Knowledge
        │                    │                     │
        └────────────────────┼─────────────────────┘
                             ▼
                     Qdrant Vector DB
                             │
               Hybrid Retrieval Pipeline
                             │
                             ▼
                       LLM Agents
```

---

# 5. Knowledge Sources

Tailr maintains multiple knowledge collections.

## Resume Knowledge

Contains

- Summary
- Experience
- Projects
- Education
- Skills
- Certifications
- Achievements

---

## Job Description Knowledge

Stores

- Previous JDs
- Company requirements
- Role expectations
- Frequently requested skills

---

## Career Knowledge

Contains

- Resume writing guides
- ATS guidelines
- Engineering resume examples
- Action verbs
- Writing best practices

---

## Resume History

Stores

- Resume versions
- ATS reports
- Generated plans
- Optimization history

---

## Feedback Knowledge

Stores

- User feedback
- Accepted changes
- Rejected suggestions

Future versions may incorporate recruiter feedback.

---

# 6. Qdrant Collections

```
qdrant

├── resume_chunks

├── skills

├── projects

├── experience

├── job_descriptions

├── resume_versions

├── career_guides

└── feedback
```

Each collection has independent embeddings.

---

# 7. Chunking Strategy

Chunking is semantic rather than fixed-size.

Bad

```
512 tokens
```

Good

```
Experience

↓

One Chunk
```

```
Project

↓

One Chunk
```

```
Skill Category

↓

One Chunk
```

Each chunk represents one complete concept.

---

# 8. Chunk Metadata

Every chunk stores metadata.

Example

```json
{
  "type": "project",
  "title": "ResearchMind",
  "technologies": ["LangChain", "FastAPI", "Python"],
  "domain": "AI",
  "years": 2026,
  "importance": 0.98
}
```

Metadata enables efficient filtering before similarity search.

---

# 9. Embedding Pipeline

```
Chunk

↓

Cleaner

↓

Metadata

↓

Embedding Model

↓

Vector

↓

Qdrant
```

Embedding Model

```
BAAI/bge-small-en-v1.5
```

Reasons

- Open Source
- Local execution
- High retrieval quality
- Fast inference

---

# 10. Retrieval Pipeline

Tailr uses hybrid retrieval.

```
Query

↓

Metadata Filter

↓

Dense Retrieval

↓

BM25 Search

↓

Merge Results

↓

Cross Encoder Reranker

↓

Top K

↓

Agent
```

---

# 11. Retrieval Types

## Dense Search

Semantic similarity using embeddings.

Suitable for

- related technologies
- responsibilities
- concepts

---

## Sparse Search

Keyword matching.

Suitable for

- exact technologies
- company names
- certifications

---

## Hybrid Search

Combines both.

Tailr uses hybrid retrieval by default.

---

# 12. Reranking

Initial retrieval returns the top 30 candidates.

These are reranked using

```
BAAI/bge-reranker-base
```

Final

Top 5

are passed to the LLM.

---

# 13. Retrieval Examples

Query

```
Backend API Development
```

Retrieved

```
FastAPI Experience

NestJS APIs

ResearchMind

REST APIs
```

---

Query

```
LLM Engineering
```

Retrieved

```
ResearchMind

LangChain

RAG

Agentic AI

Prompt Engineering
```

---

# 14. Agent Retrieval

Each agent retrieves different knowledge.

| Agent       | Retrieval Source                |
| ----------- | ------------------------------- |
| JD Analyzer | Job Description                 |
| Planner     | Resume + Skills + Career Guides |
| Rewriter    | Resume + Rewrite Plan           |
| ATS Advisor | Resume + JD + ATS Guides        |

No agent receives unnecessary context.

---

# 15. Knowledge Lifecycle

```
Upload Resume

↓

Parse

↓

Normalize

↓

Chunk

↓

Embed

↓

Store

↓

Retrieve

↓

Reason

↓

Generate

↓

Validate

↓

Archive
```

---

# 16. LlamaIndex Components

Tailr uses the following components.

### Readers

Load

- LaTeX
- Markdown
- PDF
- DOCX

---

### Node Parser

Creates semantic nodes.

---

### VectorStoreIndex

Stores vectors in Qdrant.

---

### Retriever

Performs semantic retrieval.

---

### Query Engine

Provides unified access.

---

### Workflows

Coordinates retrieval and reasoning.

---

# 17. Future Knowledge Graph

Future versions will augment vector search with graph reasoning.

```
FastAPI

↓

Python

↓

Backend

↓

API Development
```

```
ResearchMind

↓

LangChain

↓

RAG

↓

Agentic AI
```

Possible implementation

- LlamaIndex KnowledgeGraphIndex
- NetworkX
- Neo4j Community

---

# 18. Caching

Frequently accessed queries are cached.

Examples

- Backend resume
- AI Engineer resume
- React Developer resume

Caching reduces

- embedding computation
- retrieval latency
- LLM calls

---

# 19. Evaluation

Knowledge quality is measured.

Metrics

- Precision@K
- Recall@K
- MRR
- NDCG
- Context Precision
- Context Recall
- Faithfulness

Evaluation framework

```
Ragas
```

---

# 20. Security

Knowledge stores contain sensitive personal information.

Requirements

- encrypted storage
- local execution
- authenticated access
- secure deletion
- metadata validation

Resume embeddings are never shared with external services without explicit user consent.

---

# 21. Future Enhancements

The knowledge architecture is designed to evolve.

Future knowledge bases

- GitHub repositories
- LinkedIn profile
- Portfolio
- Technical blogs
- Research papers
- Interview feedback
- Recruiter conversations
- Career timeline

These sources can be indexed using the same architecture.

---

# 22. Architecture Decisions

| Decision             | Rationale                                    |
| -------------------- | -------------------------------------------- |
| Semantic chunking    | Preserves complete concepts                  |
| Multiple collections | Improves retrieval quality                   |
| Hybrid retrieval     | Combines semantic and lexical search         |
| Local embeddings     | Zero API cost                                |
| Qdrant               | Production-ready open-source vector database |
| LlamaIndex           | Native indexing and retrieval framework      |
| Reranking            | Improves context quality before generation   |

---

# 23. Summary

Tailr treats the resume as a structured knowledge system rather than a document.

The Knowledge Layer converts resumes, job descriptions, career guidance, and optimization history into searchable evidence.

Every AI decision is grounded in retrieved knowledge, validated against the canonical resume, and explainable to the user.

This architecture enables Tailr to scale from a resume optimization tool into a long-term Career Intelligence Platform without changing its foundational design.

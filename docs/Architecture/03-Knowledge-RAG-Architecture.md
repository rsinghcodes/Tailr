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

## Retrieval Before Generation

Every AI workflow must retrieve relevant context before generation.

Agents are prohibited from generating resume content solely from model knowledge.

Retrieved evidence becomes the authoritative context for all downstream reasoning, reducing hallucinations and improving explainability.

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
                             ▼
               Hybrid Retrieval Pipeline
                             │
                             ▼
                      Context Assembler
                             │
                             ▼
                         AI Agents
                             │
                             ▼
                    Guardrails Engine
                             │
                             ▼
                    Validation Engine
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

## Guardrail Knowledge

Stores deterministic validation rules used by the Guardrails Engine.

Examples

- Resume integrity policies
- Prompt injection patterns
- ATS formatting rules
- Output schemas
- Business validation policies
- Reserved keywords

Unlike semantic knowledge, Guardrail Knowledge is deterministic and version-controlled.

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

├── guardrail_rules

├── ats_rules

├── prompt_patterns

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
  "importance": 0.98,
  "source": "resume",
  "owner": "user",
  "version": 3,
  "verified": true
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

Intent Detection

↓

Metadata Filter

↓

Dense Retrieval

↓

Sparse Retrieval (BM25)

↓

Merge Results

↓

Cross Encoder Reranker

↓

Context Assembler

↓

Top K Context

↓

AI Agent

↓

Guardrails

↓

Validation
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

| Agent             | Retrieval Source                              |
| ----------------- | --------------------------------------------- |
| JD Analyzer       | Job Description                               |
| Planner           | Resume + Skills + Career Guides               |
| Rewriter          | Resume + Rewrite Plan                         |
| ATS Advisor       | Resume + JD + ATS Guides                      |
| Guardrails Engine | Guardrail Rules + ATS Rules + Prompt Patterns |

Each agent receives only the minimum context required for its task.

The Guardrails Engine retrieves deterministic policy documents instead of semantic resume content.

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

Context Assembly

↓

Reason

↓

Generate

↓

Guardrails

↓

Validation

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

### Context Assembler

Combines retrieved nodes into a deterministic context package.

Responsibilities

- remove duplicates
- preserve ordering
- enforce token limits
- attach metadata
- preserve citations

The assembled context becomes the only knowledge visible to downstream AI agents.

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

The Guardrails Engine also caches deterministic validation rules to eliminate repeated policy loading during workflow execution.

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

Additional evaluation metrics

- Context Relevance
- Retrieval Latency
- Citation Accuracy
- Hallucination Rate
- Guardrail Pass Rate
- Policy Violation Rate

These metrics help evaluate both retrieval quality and downstream AI reliability.

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

Guardrail rule sets are treated as trusted system knowledge.

They are immutable during workflow execution and may only be modified through administrative configuration or version-controlled deployments.

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

Future retrieval capabilities

- Multi-query retrieval
- Self-query retrieval
- Agent-specific retrievers
- Graph-enhanced retrieval
- Temporal retrieval
- Personalized ranking
- Context compression

---

# 22. Architecture Decisions

| Decision                 | Rationale                                            |
| ------------------------ | ---------------------------------------------------- |
| Semantic chunking        | Preserves complete concepts                          |
| Multiple collections     | Improves retrieval quality                           |
| Hybrid retrieval         | Combines semantic and lexical search                 |
| Local embeddings         | Zero API cost                                        |
| Qdrant                   | Production-ready open-source vector database         |
| LlamaIndex               | Native indexing and retrieval framework              |
| Reranking                | Improves context quality before generation           |
| Context Assembler        | Produces deterministic context packages              |
| Guardrail Knowledge      | Separates AI safety policies from semantic knowledge |
| Agent-specific Retrieval | Minimizes unnecessary context                        |
| Metadata-first Filtering | Metadata-first Filtering                             |

---

# 23. Summary

Tailr treats the resume as a structured knowledge system rather than a document.

The Knowledge Layer converts resumes, job descriptions, career guidance, and optimization history into searchable evidence.

Every AI decision is grounded in retrieved knowledge, validated against the canonical resume, processed through the Guardrails Engine, and verified by deterministic business validation before being returned to the user.

This layered architecture separates retrieval, reasoning, AI safety, and business validation, enabling Tailr to scale into a comprehensive Career Intelligence Platform while maintaining explainability, reliability, and production-grade robustness.

# ADR-0005: Use LlamaIndex as the AI Data Framework

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr is an AI-native resume optimization platform that relies on Retrieval-Augmented Generation (RAG) to provide accurate, context-aware resume improvements.

The system must:

- Parse resumes
- Build searchable knowledge
- Generate embeddings
- Index structured information
- Retrieve relevant context
- Orchestrate retrieval pipelines
- Support multiple LLMs
- Evaluate retrieval quality
- Enable future AI workflows

Building these capabilities from scratch would significantly increase complexity and maintenance costs.

A dedicated AI framework is required to manage the complete data flow between application data and language models.

---

# Decision

Tailr adopts **LlamaIndex** as the primary AI data framework.

LlamaIndex is responsible for:

- Document ingestion
- Chunk creation
- Embedding generation
- Index management
- Retrieval pipelines
- Query orchestration
- LLM abstraction
- Evaluation utilities

Business logic remains outside LlamaIndex.

---

# Decision Drivers

The selected framework must:

- Be open source
- Support local LLMs
- Integrate with Qdrant
- Support multiple embedding models
- Provide modular architecture
- Enable custom retrieval pipelines
- Work well with structured documents
- Support future AI workflows

---

# Architectural Role

```
            Resume
               │
               ▼
      Resume Parser
               │
               ▼
 Canonical Resume Model
               │
               ▼
        LlamaIndex
               │
      ┌────────┴────────┐
      ▼                 ▼
Embedding Model     Qdrant
      │                 │
      └────────┬────────┘
               ▼
        Retrieval Engine
               │
               ▼
             LLM
```

LlamaIndex acts as the bridge between structured knowledge and AI reasoning.

---

# Responsibilities

LlamaIndex manages:

- Document ingestion
- Node generation
- Metadata attachment
- Embedding creation
- Vector indexing
- Retrieval
- Context assembly
- Response synthesis

The application remains responsible for orchestration and business rules.

---

# Retrieval Pipeline

```
Job Description
        │
        ▼
Query Generation
        │
        ▼
Embedding
        │
        ▼
Vector Search
        │
        ▼
Metadata Filtering
        │
        ▼
Top-K Nodes
        │
        ▼
Context Assembly
        │
        ▼
LLM Prompt
```

Each stage is configurable.

---

# Metadata Strategy

Every indexed node contains metadata such as:

```json
{
  "resume_id": "res_001",
  "section": "projects",
  "project": "ResearchMind",
  "skills": ["FastAPI", "LangChain", "Qdrant"],
  "version": 3
}
```

Metadata enables filtered retrieval and ownership enforcement.

---

# Embedding Strategy

Embedding models are abstracted.

Initial options include:

- BAAI/bge-small-en-v1.5
- BAAI/bge-base-en-v1.5
- nomic-embed-text
- Snowflake Arctic Embed

The embedding model can change without affecting application logic.

---

# Vector Store Integration

LlamaIndex integrates directly with Qdrant.

Responsibilities include:

- Create vectors
- Update vectors
- Delete vectors
- Query vectors
- Apply metadata filters

Qdrant remains the storage engine.

---

# Query Engine

The query engine performs:

```
Receive Query

↓

Embed Query

↓

Retrieve Candidates

↓

Filter Results

↓

Rank Results

↓

Assemble Context

↓

Generate Response
```

The query engine is configurable and extensible.

---

# Evaluation Support

LlamaIndex provides evaluation utilities for:

- Retrieval accuracy
- Context relevance
- Response quality
- Faithfulness
- Hallucination detection

Evaluation metrics are integrated into Tailr's testing framework.

---

# Multi-LLM Support

LlamaIndex abstracts model providers.

Supported providers include:

- Ollama
- OpenAI
- Anthropic
- Hugging Face Inference
- Future providers

Changing the underlying model requires minimal application changes.

---

# Alternatives Considered

## Option 1 — Build Custom RAG

### Advantages

- Complete control
- Minimal dependencies

### Disadvantages

- High development effort
- Reinvents existing functionality
- Difficult maintenance
- Limited evaluation support

Decision: Rejected

---

## Option 2 — LangChain

### Advantages

- Large ecosystem
- Mature agent framework
- Extensive integrations

### Disadvantages

- Broader focus on orchestration than data
- More abstraction for simple RAG pipelines
- Frequent API evolution

Decision: Partially Rejected

LangChain may be introduced later for advanced agent orchestration, but not as the primary data framework.

---

## Option 3 — Haystack

### Advantages

- Mature search pipelines
- Strong enterprise adoption

### Disadvantages

- Heavier setup
- Less aligned with the project's local-first goals

Decision: Rejected

---

## Option 4 — LlamaIndex

### Advantages

- Purpose-built for RAG
- Excellent document indexing
- Native Qdrant integration
- Flexible retrieval pipelines
- Strong evaluation tools
- Active open-source community

### Disadvantages

- Additional abstraction layer
- Requires understanding of indexing concepts

Decision: Accepted

---

# Consequences

## Positive

- Faster development
- Better retrieval quality
- Modular architecture
- Easier model replacement
- Built-in evaluation support
- Simplified vector management

---

## Negative

- Dependency on external framework
- Learning curve for contributors
- Framework upgrades require compatibility testing

---

# Risks

| Risk                      | Mitigation                               |
| ------------------------- | ---------------------------------------- |
| API changes               | Pin package versions and review upgrades |
| Framework lock-in         | Keep business logic independent          |
| Retrieval regressions     | Automated evaluation datasets            |
| Embedding incompatibility | Abstract embedding providers             |

---

# Architecture Integration

```
FastAPI

↓

Application Layer

↓

Workflow Engine

↓

LlamaIndex

↓

Qdrant + Ollama

↓

LLM Response
```

LlamaIndex remains an infrastructure component and does not contain business rules.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture
- ADR-0003 — Use FastAPI as the Primary Backend Framework
- ADR-0004 — Use PostgreSQL as the Primary Database
- ADR-0006 — Use Qdrant as the Vector Database
- ADR-0007 — Adopt a Multi-Agent Workflow

---

# References

- RAG-Architecture.md
- Knowledge-Model.md
- Workflow-Design.md
- Data-Models.md
- Testing.md

---

# Review Notes

This decision should be revisited if:

- retrieval requirements significantly exceed the framework's capabilities,
- the project adopts a different AI data abstraction,
- or operational complexity outweighs the productivity benefits.

Until then, LlamaIndex remains the standard AI data framework for indexing, retrieval, and context construction within Tailr.

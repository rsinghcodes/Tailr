# RAG Module — Production Implementation Prompt

## Objective

Implement the complete production-ready **RAG Module** for Tailr.

This module provides the knowledge retrieval pipeline that grounds every AI decision in retrieved evidence rather than relying on LLM internal knowledge.

The RAG Module is responsible for:

- semantic chunking,
- embedding generation,
- vector store abstraction,
- hybrid retrieval (dense + sparse),
- cross-encoder reranking,
- prompt-injection scanning of retrieved context,
- context assembly,
- prompt building,
- caching,
- retrieval metrics,
- and LlamaIndex integration.

Every retrieval stage must be independently replaceable.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/rag.md
- rules/security.md
- rules/testing.md
- rules/logging.md
- ADR-0002 — Clean Architecture
- ADR-0005 — Use LlamaIndex
- ADR-0011 — Validation & Guardrails Engine
- 03-Knowledge-RAG-Architecture.md
- 04-Knowledge-Model.md
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Architecture Constraints

The RAG pipeline has **two distinct Guardrails checkpoints**:

1. **Retrieval stage** — prompt-injection scan on retrieved context before it enters a prompt
2. **Generation stage** — full guardrail validation on LLM output (handled downstream by the workflow/agent layer)

Neither checkpoint substitutes for the other. Neither is optional.

---

# Chunking

Implement semantic chunking (not fixed-size).

### Strategy

- one complete concept per chunk
- experience entry → one chunk
- project → one chunk
- skill category → one chunk
- education entry → one chunk

### Configuration

- target size: **500-800 tokens**
- overlap: **50-100 tokens** (configurable)

### Chunk Metadata

Every chunk must include:

```python
ChunkMetadata(
    entity_type: str,       # project, experience, skill, education
    entity_id: str,
    title: str,
    technologies: list[str],
    domain: str,
    importance: float,
    source: str,            # resume, career_guide, job_description
    owner: str,
    version: int,
    verified: bool,
    created_at: datetime,
)
```

---

# Embedding Pipeline

```text
Chunk → Cleaner → Metadata → Embedding Model → Vector → Qdrant
```

### Embedding Model

- Default: `BAAI/bge-small-en-v1.5`
- Local execution (no external API)
- Configurable model, dimension, batch_size, device

### Requirements

- centralized embedding provider (never duplicate logic)
- batch embedding support
- normalize embeddings
- cache embeddings

---

# Vector Store Abstraction

Never call Qdrant directly from services.

### Interface

```python
class VectorStore(Protocol):
    async def upsert(self, collection: str, vectors: list[VectorRecord]) -> None: ...
    async def search(self, collection: str, query_vector: list[float], top_k: int, filters: dict | None) -> list[SearchResult]: ...
    async def delete(self, collection: str, ids: list[str]) -> None: ...
    async def create_collection(self, collection: str, dimension: int) -> None: ...
    async def health_check(self) -> HealthStatus: ...
```

### Implementations

- `QdrantVectorStore`
- `FAISSVectorStore` (future)
- `ChromaVectorStore` (future)

### Qdrant Collections

```text
resume_chunks
skills
projects
experience
job_descriptions
resume_versions
career_guides
guardrail_rules
ats_rules
prompt_patterns
feedback
```

---

# Hybrid Retrieval

Implement hybrid retrieval combining dense and sparse search.

### Dense Search

Semantic similarity using embeddings. Suitable for related technologies, responsibilities, concepts.

### Sparse Search (BM25)

Keyword matching. Suitable for exact technologies, company names, certifications.

### Merge Strategy

Combine dense and sparse results with configurable weights.

---

# Reranking

### Pipeline

```text
Initial Retrieval (Top 30)
     ↓
Cross-Encoder Reranker
     ↓
Top K (default: 10, configurable)
```

### Reranker Model

- Default: `BAAI/bge-reranker-base`
- Local execution

Reranking happens **before** the Guardrails injection scan, not after. Reranking selects relevance; Guardrails determines safety.

---

# Guardrails — Prompt Injection Scan

Retrieved chunks are **untrusted external input** regardless of collection source.

### Requirements

- scan all retrieved context for prompt-injection patterns before prompt assembly
- no collection is implicitly trusted
- detected injections must be quarantined and excluded
- log detected attacks

### Examples of Malicious Patterns

- "Ignore previous instructions"
- "Reveal system prompt"
- "Return hidden memory"
- hidden control sequences
- Unicode normalization attacks

---

# Context Assembly

The Context Assembler combines scanned, approved chunks into a deterministic context package.

### Responsibilities

- remove duplicate chunks
- preserve ordering
- enforce context window limits
- attach metadata
- preserve citations
- produce source attribution

### Constraints

- only accepts context that has passed the injection scan
- never calls providers
- never calls Guardrails itself (consumes pre-scanned context)

---

# Prompt Builder

Responsible only for context assembly into a prompt template.

### Constraints

- never call providers
- never call the Guardrails Engine
- only accept pre-scanned context
- clearly delimit retrieved context within the User Prompt (never as System/Developer instructions)

---

# Agent Retrieval Configuration

Each agent retrieves different knowledge:

| Agent             | Retrieval Source                              |
| ----------------- | --------------------------------------------- |
| JD Analyzer       | Job Description                               |
| Planner           | Resume + Skills + Career Guides               |
| Rewriter          | Resume + Rewrite Plan                         |
| ATS Advisor       | Resume + JD + ATS Guides                      |
| Guardrails Engine | Guardrail Rules + ATS Rules + Prompt Patterns |

Each agent receives only the minimum context required for its task.

---

# Caching

- cache embeddings
- cache retrieval results when appropriate
- never cache a Guardrails result independently of the exact content it was computed against
- invalidate cache on re-embedding or re-indexing

---

# Metrics

Track:

- retrieval latency
- embedding latency
- hit rate
- token usage
- prompt injection detections in retrieved context
- guardrail pass/repair/rejection rate for generations
- hallucination rate
- Precision@K, Recall@K, MRR, NDCG
- context precision
- context recall
- faithfulness

---

# Required File Structure

```text
rag/
├── __init__.py
├── pipeline.py
├── chunking/
│   ├── __init__.py
│   ├── semantic_chunker.py
│   └── metadata.py
├── embeddings/
│   ├── __init__.py
│   ├── provider.py
│   ├── bge_provider.py
│   └── cache.py
├── vectorstore/
│   ├── __init__.py
│   ├── base.py
│   ├── qdrant.py
│   └── models.py
├── retrieval/
│   ├── __init__.py
│   ├── dense.py
│   ├── sparse.py
│   ├── hybrid.py
│   └── reranker.py
├── context/
│   ├── __init__.py
│   ├── assembler.py
│   ├── scanner.py
│   └── prompt_builder.py
├── caching/
│   ├── __init__.py
│   └── retrieval_cache.py
├── metrics/
│   ├── __init__.py
│   └── evaluation.py
└── exceptions.py
```

---

# Testing Requirements

Generate tests for:

- semantic chunking (entity-boundary preservation),
- embedding generation (batch, single),
- vector store operations (upsert, search, delete),
- hybrid retrieval (dense only, sparse only, combined),
- reranking (ordering, top-k cutoff),
- prompt injection scanning (known attack patterns, clean context),
- context assembly (deduplication, token limits, citations),
- caching (hit, miss, invalidation),
- retrieval metrics (precision, recall, MRR),
- end-to-end pipeline tests,
- and performance benchmarks.

Use: pytest, pytest-asyncio, Testcontainers (Qdrant), mock embedding providers.

Target coverage: **90%+**.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- separate abstractions from implementations,
- be async-first,
- avoid global mutable state,
- and be production deployable.

---

# Output Requirements

Return:

1. complete source files,
2. test files,
3. chunking strategy explanation,
4. retrieval pipeline diagram,
5. embedding model selection rationale,
6. injection scanning explanation,
7. caching strategy explanation,
8. evaluation metrics documentation,
9. configuration examples,
10. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready RAG Module** that provides:

- semantic chunking,
- local embeddings,
- vector store abstraction,
- hybrid retrieval with reranking,
- prompt-injection scanning,
- deterministic context assembly,
- caching,
- retrieval evaluation metrics,
- and comprehensive testing

for the Tailr platform.

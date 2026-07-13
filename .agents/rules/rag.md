# RAG Rules

Priority: HIGH

---

Pipeline

Parser

↓

Cleaner

↓

Chunker

↓

Embedding

↓

Vector Store

↓

Retriever

↓

Reranker

↓

Prompt Builder

↓

LLM

↓

Validator

---

Chunking

Semantic chunks preferred.

Target size

500-800 tokens

Overlap

50-100 tokens

---

Embeddings

Centralized provider.

Never duplicate embedding logic.

---

Vector Store

Use interface

VectorStore

Implementations

Qdrant

FAISS

Chroma

---

Retrieval

Top K configurable.

Default

10

---

Reranking

Always rerank before prompt assembly.

---

Prompt Builder

Responsible only for context assembly.

Never call providers.

---

Caching

Cache embeddings.

Cache retrieval when appropriate.

---

Validation

Remove duplicate chunks.

Respect context window.

Preserve citations.

---

Metrics

Track

Retrieval latency

Embedding latency

Hit rate

Token usage

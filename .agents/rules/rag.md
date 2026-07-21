---
trigger: always_on
---

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

Guardrails (prompt-injection scan on retrieved context)

↓

Prompt Builder

↓

LLM

↓

Guardrails (schema, hallucination, integrity, PII, ATS, LaTeX safety, repair)

↓

Validator

The pipeline has two distinct Guardrails checkpoints, not one. The first protects the prompt from injected instructions hiding in retrieved content. The second protects everything downstream from the LLM's raw output. Neither checkpoint substitutes for the other, and neither is optional.

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

Retrieved chunks are untrusted the moment they leave the Vector Store, regardless of collection. A chunk sourced from `job_descriptions` or `career_guides` is external content and receives the same injection scan as a chunk from any other source — no collection is implicitly trusted.

---

Reranking

Always rerank before prompt assembly.

Reranking happens before the Guardrails injection scan, not after. Reranking selects which chunks are relevant; Guardrails determines whether the selected chunks are safe to include. Do not skip the scan on the assumption that a highly-relevant chunk is also a safe one.

---

Prompt Builder

Responsible only for context assembly.

Never call providers.

Never call the Guardrails Engine itself. The Prompt Builder consumes context that has already been scanned and approved upstream — it assembles the prompt, it does not decide what is safe to assemble.

Only accepts context that has already passed the retrieval-stage Guardrails scan. If a caller attempts to pass unscanned chunks directly to the Prompt Builder, that is a pipeline-ordering bug.

---

Caching

Cache embeddings.

Cache retrieval when appropriate.

Never cache a Guardrails result independently of the exact content it was computed against. A cached chunk that later gets re-embedded or re-indexed must be re-scanned, not served with a stale approval.

---

Validation

Remove duplicate chunks.

Respect context window.

Preserve citations.

These checks happen in addition to, not instead of, the Guardrails prompt-injection scan. Deduplication and context-window enforcement are RAG-quality concerns; injection scanning is an AI-safety concern — do one without skipping the other.

---

Metrics

Track

Retrieval latency

Embedding latency

Hit rate

Token usage

Prompt injection detections in retrieved context

Guardrail pass / repair / rejection rate for generations produced from this pipeline

Hallucination rate (generated content not grounded in the Canonical Resume Model, despite retrieval having supplied relevant context)

A rising hallucination rate despite stable retrieval precision is a signal to investigate the Prompt Builder or the generation prompt, not the retriever — track them as separate metrics so root cause isn't ambiguous.

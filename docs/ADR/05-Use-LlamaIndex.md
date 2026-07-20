# ADR-0005: Use LlamaIndex as the AI Data and Workflow Framework

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr is an AI-native Resume Intelligence Platform that relies on **Retrieval-Augmented Generation (RAG)** and **agentic workflows** to provide accurate, context-aware resume optimizations.

The system must:

- Parse resumes
- Build searchable knowledge
- Generate embeddings
- Index structured information
- Retrieve relevant context
- Apply metadata filtering
- Rerank retrieved results
- Assemble token-efficient prompts
- Orchestrate multi-step AI workflows
- Support multiple LLM providers
- Evaluate retrieval quality
- Support future AI capabilities

Building these capabilities from scratch would significantly increase development effort, operational complexity, and maintenance cost.

A dedicated framework is required to manage the complete flow between **structured application data** and **language models**.

---

# Decision

Tailr will use **LlamaIndex** as the primary **AI data and workflow framework**.

LlamaIndex is responsible for:

- Document ingestion
- Semantic chunking
- Embedding generation
- Index management
- Retrieval pipelines
- Hybrid search orchestration
- Context assembly
- LLM abstraction
- Workflow orchestration
- Evaluation utilities

Business logic remains outside LlamaIndex and is implemented in the **Application** and **Domain** layers defined in ADR-0002.

LlamaIndex is treated as an **Infrastructure Adapter**, not a domain dependency.

---

# Decision Drivers

The selected framework must:

- be open source,
- support local LLMs,
- integrate with Qdrant Cloud,
- support multiple embedding models,
- provide modular retrieval pipelines,
- support metadata filtering,
- support reranking,
- work well with structured documents,
- support asynchronous workflows,
- provide evaluation tooling,
- enable future AI workflows.

---

# Architectural Role

<CodeBlock language="text" content="Resume
│
▼
Resume Parser
│
▼
Canonical Resume Model
│
▼
Knowledge Layer
│
▼
LlamaIndex
│
├── Embedding Provider
├── Qdrant Vector Store
├── Hybrid Retriever
├── Reranker
└── Workflow Engine
        │
        ▼
   AI Agents
        │
        ▼
   Guardrails
        │
        ▼
 Validation Engine"/>

LlamaIndex acts as the bridge between **structured knowledge** and **AI reasoning**.

---

# Responsibilities

LlamaIndex manages:

- document ingestion,
- semantic chunk creation,
- metadata attachment,
- embedding creation,
- vector indexing,
- retrieval orchestration,
- metadata filtering,
- reranking,
- context assembly,
- workflow state transitions,
- response synthesis,
- retrieval evaluation.

The application remains responsible for:

- business policies,
- resume integrity,
- ATS scoring,
- guardrail decisions,
- persistence,
- deterministic rendering.

---

# Retrieval Pipeline

Tailr uses a **hybrid retrieval pipeline**.

<CodeBlock language="text" content="Job Description
   │
   ▼
Query Builder
   │
   ▼
Query Embedding
   │
   ├── Dense Search (Qdrant)
   └── Sparse Search (BM25)
            │
            ▼
       Merge Results
            │
            ▼
         Reranker
            │
            ▼
      Top-K Context
            │
            ▼
     Context Builder
            │
            ▼
      Structured Prompt"/>

Each stage is independently configurable.

---

# Metadata Strategy

Every indexed node contains metadata such as:

<CodeBlock language="json" content="{
"resume_id": "res_001",
"section": "projects",
"project": "ResearchMind",
"skills": ["FastAPI", "LangChain", "Qdrant"],
"version": 3,
"date_range": "2026-01:2026-03"
}"/>

Metadata enables:

- section filtering,
- version isolation,
- ownership enforcement,
- skill-based retrieval,
- temporal filtering,
- auditability.

---

# Embedding Strategy

Embedding providers are abstracted behind interfaces.

Initial models include:

- `BAAI/bge-small-en-v1.5`
- `BAAI/bge-base-en-v1.5`
- `nomic-embed-text`
- `Snowflake Arctic Embed`

The embedding model can be replaced without affecting application logic or database schemas.

---

# Vector Store Integration

LlamaIndex integrates directly with **Qdrant Cloud**.

Responsibilities:

- create vectors,
- update vectors,
- delete vectors,
- execute similarity search,
- apply metadata filters,
- manage collection schemas.

Qdrant remains the **storage engine**; LlamaIndex remains the **orchestration layer**.

---

# Workflow Engine

Tailr uses **LlamaIndex Workflows** for orchestrating AI pipelines.

Example:

<CodeBlock language="text" content="Parse Resume
   ↓
Index Knowledge
   ↓
Generate Plan
   ↓
Retrieve Context
   ↓
Rewrite Content
   ↓
Run Guardrails
   ↓
Validate
   ↓
Generate ATS Report
   ↓
Render PDF"/>

Benefits:

- typed events,
- async execution,
- retry support,
- workflow observability,
- state tracking,
- easier testing.

---

# Context Assembly

LlamaIndex assembles token-efficient context windows.

The Context Builder:

- removes duplicates,
- prioritizes recent experience,
- preserves section boundaries,
- enforces token budgets,
- attaches evidence references,
- returns structured context objects.

This improves determinism and reduces hallucination risk.

---

# Guardrails Integration

LlamaIndex does **not** enforce business validation.

All generated outputs are passed to the **Guardrails Layer** for:

- JSON validation,
- schema validation,
- prompt injection detection,
- hallucination detection,
- resume integrity checks,
- ATS formatting validation.

Guardrails remain outside LlamaIndex to avoid framework lock-in.

---

# Evaluation Support

LlamaIndex provides evaluation utilities for:

- retrieval precision,
- recall@k,
- context relevance,
- answer faithfulness,
- response quality,
- latency analysis.

These metrics are integrated into Tailr’s evaluation pipeline and CI/CD quality gates.

---

# Multi-LLM Support

LlamaIndex abstracts model providers.

Supported providers include:

- Ollama
- OpenAI
- Anthropic
- Google Gemini
- Hugging Face Inference
- future custom providers

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
- Slower feature development

**Decision:** Rejected

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
- Heavier dependency surface

**Decision:** Partially Rejected

LangChain may be introduced later for specialized orchestration, but not as the primary data framework.

---

## Option 3 — Haystack

### Advantages

- Mature search pipelines
- Strong enterprise adoption

### Disadvantages

- Heavier setup
- Less aligned with local-first architecture
- Smaller workflow ecosystem

**Decision:** Rejected

---

## Option 4 — LlamaIndex

### Advantages

- Purpose-built for RAG
- Excellent document indexing
- Native Qdrant integration
- Flexible retrieval pipelines
- Strong evaluation tooling
- Built-in workflow engine
- Active open-source community

### Disadvantages

- Additional abstraction layer
- Requires understanding of indexing concepts
- Workflow APIs require discipline

**Decision:** Accepted

---

# Consequences

## Positive

- Faster development
- Better retrieval quality
- Modular architecture
- Easier model replacement
- Built-in evaluation support
- Simplified vector management
- Native workflow orchestration
- Better observability hooks

---

## Negative

- Dependency on an external framework
- Learning curve for contributors
- Framework upgrades require compatibility testing
- Some advanced behavior may require custom extensions

---

# Risks

| Risk                      | Mitigation                               |
| ------------------------- | ---------------------------------------- |
| API changes               | Pin package versions and review upgrades |
| Framework lock-in         | Keep business logic independent          |
| Retrieval regressions     | Automated evaluation datasets            |
| Embedding incompatibility | Abstract embedding providers             |
| Workflow API changes      | Isolate workflow adapters                |
| Performance overhead      | Benchmark and profile retrieval stages   |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
Application Layer
│
▼
Workflow Orchestrator
│
▼
LlamaIndex
│
├── Qdrant Cloud
├── Embedding Provider
├── Reranker
└── LLM Provider
        │
        ▼
   Guardrails
        │
        ▼
 Validation Engine
        │
        ▼
  Structured Result"/>

LlamaIndex remains an **Infrastructure component** and does not contain business rules.

---

# Future Evolution

The following capabilities can be added incrementally:

- graph-based retrieval,
- knowledge graph indexes,
- long-term memory,
- conversational retrieval,
- personalized ranking,
- feedback-aware retrieval,
- multi-document reasoning,
- distributed workflow execution.

The surrounding architecture isolates these changes from the Domain layer.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture with Hexagonal Boundaries
- ADR-0003 — Use FastAPI as the Primary Backend Framework
- ADR-0004 — Use PostgreSQL as the Primary Transactional Database
- ADR-0006 — Adopt a Multi-Agent Workflow
- ADR-0008 — Adopt a Validation & Guardrails Engine

---

# References

- rag-architecture.md
- knowledge-model.md
- workflow-design.md
- data-models.md
- testing.md
- evaluation-architecture.md
- guardrails-architecture.md

---

# Review Notes

This decision should be revisited if:

- retrieval requirements significantly exceed the framework’s capabilities,
- a different AI data abstraction becomes strategically preferable,
- workflow orchestration needs exceed LlamaIndex capabilities,
- or operational complexity outweighs the productivity benefits.

Until then, **LlamaIndex remains the standard AI data and workflow framework for indexing, retrieval, context construction, and workflow orchestration within Tailr**.

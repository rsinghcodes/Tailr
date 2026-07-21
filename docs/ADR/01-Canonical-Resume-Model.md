# ADR-0001: Adopt a Canonical Resume Model as the System Source of Truth

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr is an AI-native Resume Intelligence Platform whose primary input and output format is LaTeX.

However, the platform performs significantly more than simple text editing.

It must:

- understand resume structure
- analyze projects and experience
- retrieve relevant professional history
- optimize content for ATS
- validate generated content
- enforce AI safety guardrails
- support immutable versioning
- compare resume revisions
- generate deterministic PDFs
- support future document formats

If the system manipulates raw LaTeX directly, every AI component must understand LaTeX syntax and formatting semantics.

Example:

```latex
\resumeProjectHeading
{ResearchMind}{2026}
```

For an LLM, this is primarily formatting rather than structured meaning.

Supporting DOCX, Markdown, JSON resumes, or future formats would require rewriting most of the platform if LaTeX remained the internal representation.

The system therefore requires a technology-independent, structured internal representation that becomes the canonical source of truth.

---

# Decision

Tailr will introduce a **Canonical Resume Model (CRM)**.

Every resume uploaded to the platform will follow this pipeline:

```text
LaTeX / DOCX / Markdown Resume
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
      RAG + Agents
            │
            ▼
       Guardrails
            │
            ▼
  Business Validation
            │
            ▼
Updated Canonical Resume
            │
            ▼
     Rendering Engine
            │
            ▼
        LaTeX Output
            │
            ▼
       PDF Generation
```

The **Canonical Resume Model becomes the single source of truth** for all downstream components.

No AI agent, workflow, or business service may directly manipulate LaTeX templates.

---

# Decision Drivers

This decision is driven by the following requirements:

- Separation of content and presentation
- AI-friendly structured data
- Deterministic validation
- Multi-format document support
- Long-term maintainability
- Easier testing
- Better retrieval quality
- Immutable resume versioning
- Guardrail enforcement
- Prompt injection resilience
- Explainable optimization workflows

---

# Canonical Resume Structure

The model contains structured entities such as:

- Personal Information
- Summary
- Experience
- Projects
- Skills
- Education
- Certifications
- Publications
- Awards
- Metadata
- Resume Version Metadata

Each entity contains semantic information instead of presentation logic.

Example:

```json
{
  "project": {
    "title": "ResearchMind",
    "description": "AI-powered research assistant",
    "technologies": ["FastAPI", "LangChain", "Qdrant"],
    "start_date": "2026-01",
    "end_date": "2026-03"
  }
}
```

The canonical schema is versioned independently of storage and rendering formats.

---

# Guardrails Integration

Every AI-generated modification must pass through the Guardrails pipeline before being applied to the canonical model.

Pipeline:

```text
LLM Output
    │
    ▼
JSON Validation
    │
    ▼
Schema Validation
    │
    ▼
Prompt Injection Detection
    │
    ▼
Hallucination Detection
    │
    ▼
Resume Integrity Validation
    │
    ▼
ATS Validation
    │
    ▼
Business Validation
```

The CRM enables deterministic comparison between generated content and the original resume, making hallucination detection practical and reliable.

---

# Alternatives Considered

## Option 1 — Edit Raw LaTeX

### Advantages

- Simple implementation
- No parsing layer

### Disadvantages

- LLM must understand LaTeX
- Difficult validation
- High hallucination risk
- Template-dependent logic
- Poor extensibility
- Fragile formatting
- Hard to enforce guardrails

**Decision:** Rejected

---

## Option 2 — Edit PDF

### Advantages

- No parsing required

### Disadvantages

- Content extraction is unreliable
- Formatting information is incomplete
- Difficult to reconstruct structure
- Unsuitable for semantic editing

**Decision:** Rejected

---

## Option 3 — Convert to Markdown

### Advantages

- Easier for LLMs

### Disadvantages

- Loss of formatting fidelity
- Difficult round-trip conversion
- Weak structural guarantees
- Ambiguous section boundaries

**Decision:** Rejected

---

## Option 4 — Canonical Resume Model

### Advantages

- AI-friendly
- Format-independent
- Easy validation
- Better testing
- Better retrieval
- Future-proof architecture
- Enables guardrails
- Enables immutable versioning
- Enables deterministic rendering

### Disadvantages

- Parser complexity
- Renderer complexity
- Schema evolution management
- Initial development effort

**Decision:** Accepted

---

# Consequences

## Positive

The CRM enables:

- Structured RAG retrieval
- Deterministic validation
- Guardrail enforcement
- Better prompt engineering
- Immutable resume versioning
- Template independence
- Cleaner business logic
- Easier unit testing
- Future support for DOCX, Markdown, and JSON resumes
- Explainable optimization workflows
- Improved maintainability

---

## Negative

The system must maintain:

- Resume parser
- Rendering engine
- Canonical schema
- Schema migrations
- Validation rules
- Guardrail policies
- Backward compatibility logic

These components increase development effort and operational complexity.

---

# Risks

| Risk                      | Mitigation                          |
| ------------------------- | ----------------------------------- |
| Parser bugs               | Golden test dataset                 |
| Schema evolution          | Versioned schema                    |
| Rendering inconsistencies | Snapshot testing                    |
| Performance overhead      | Parser caching                      |
| New template support      | Plugin-based parser architecture    |
| Guardrail false positives | Configurable validation policies    |
| Migration complexity      | Backward-compatible schema adapters |

---

# Impact

This decision directly affects:

- Resume Parser
- Knowledge Layer
- RAG Pipeline
- Agent Framework
- Guardrails Engine
- Validation Engine
- ATS Engine
- Rendering Engine
- PDF Compiler
- Version Control
- Database Schema
- API Contracts
- Evaluation Pipeline

Nearly every major subsystem depends on this architectural decision.

---

# Related ADRs

- ADR-0002 — Use FastAPI as the Backend Framework
- ADR-0003 — Use PostgreSQL as the Primary Database
- ADR-0004 — Use Qdrant as the Vector Database
- ADR-0005 — Use LlamaIndex as the RAG and Knowledge Framework
- ADR-0006 — Adopt a Multi-Agent Workflow
- ADR-0008 — Adopt a Validation & Guardrails Engine

---

# References

- system-architecture.md
- parser-architecture.md
- knowledge-model.md
- data-models.md
- rag-architecture.md
- workflow-design.md
- guardrails-architecture.md

---

# Review Notes

This decision should be revisited if:

- the platform no longer supports multiple resume formats,
- parser maintenance becomes prohibitively expensive,
- a fundamentally different document representation proves superior, or
- guardrail enforcement becomes impossible to maintain at the CRM boundary.

Until then, the **Canonical Resume Model remains the architectural foundation of Tailr and the authoritative representation of all resume data**.

# ADR-0001: Adopt a Canonical Resume Model as the System Source of Truth

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr is an AI-native resume optimization platform whose primary input and output format is LaTeX.

However, the platform must perform much more than simple text editing.

It needs to:

- understand resume structure
- analyze projects
- retrieve relevant experience
- optimize content for ATS
- validate generated content
- support versioning
- compare resume revisions
- generate PDFs
- support future document formats

If the system manipulates raw LaTeX directly, every AI component must understand LaTeX syntax.

Example:

```latex
\resumeProjectHeading
{ResearchMind}{2026}
```

For an LLM, this is formatting rather than meaning.

Similarly, supporting DOCX, Markdown, or JSON resumes in the future would require rewriting most of the platform.

The system therefore requires a technology-independent internal representation.

---

# Decision

Tailr will introduce a **Canonical Resume Model (CRM)**.

Every resume uploaded to the platform will follow this pipeline:

```
LaTeX Resume
        │
        ▼
Resume Parser
        │
        ▼
Canonical Resume Model
        │
        ▼
Knowledge Graph
        │
        ▼
RAG + Agents
        │
        ▼
Updated Canonical Resume Model
        │
        ▼
LaTeX Renderer
        │
        ▼
Optimized Resume
```

The Canonical Resume Model becomes the single source of truth for all downstream components.

No AI agent or business service may directly manipulate LaTeX.

---

# Decision Drivers

The decision is driven by the following requirements:

- Separation of content and presentation
- AI-friendly structured data
- Deterministic validation
- Multi-format document support
- Long-term maintainability
- Easier testing
- Better retrieval quality
- Immutable resume versioning

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

Each entity contains semantic information instead of presentation logic.

Example:

```json
{
  "project": {
    "title": "ResearchMind",
    "description": "...",
    "technologies": ["FastAPI", "LangChain", "Qdrant"]
  }
}
```

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

Decision: Rejected

---

## Option 2 — Edit PDF

### Advantages

- No parsing required

### Disadvantages

- Content extraction is unreliable
- Formatting information is incomplete
- Difficult to reconstruct structure
- Unsuitable for semantic editing

Decision: Rejected

---

## Option 3 — Convert to Markdown

### Advantages

- Easier for LLMs

### Disadvantages

- Loss of formatting fidelity
- Difficult round-trip conversion
- Weak structural guarantees

Decision: Rejected

---

## Option 4 — Canonical Resume Model

### Advantages

- AI-friendly
- Format-independent
- Easy validation
- Better testing
- Better retrieval
- Future-proof architecture

### Disadvantages

- Parser complexity
- Renderer complexity
- Initial development effort

Decision: Accepted

---

# Consequences

## Positive

The Canonical Resume Model enables:

- Structured RAG retrieval
- Deterministic validation
- Better prompt engineering
- Immutable resume versioning
- Template independence
- Cleaner business logic
- Easier unit testing
- Future support for DOCX, Markdown, and JSON resumes
- Improved maintainability

---

## Negative

The system must now maintain:

- Parser
- Renderer
- Canonical schema
- Schema migrations
- Validation rules

These components increase development effort.

---

# Risks

| Risk                      | Mitigation                       |
| ------------------------- | -------------------------------- |
| Parser bugs               | Golden test dataset              |
| Schema evolution          | Versioned schema                 |
| Rendering inconsistencies | Snapshot testing                 |
| Performance overhead      | Parser caching                   |
| New template support      | Plugin-based parser architecture |

---

# Impact

This decision directly affects:

- Resume Parser
- Knowledge Builder
- RAG Pipeline
- Agent Framework
- Validation Engine
- ATS Scoring
- PDF Renderer
- Version Control
- Database Schema
- API Contracts

Nearly every major subsystem depends on this architecture.

---

# Related ADRs

- ADR-0002 — Use FastAPI as the Backend Framework
- ADR-0003 — Use PostgreSQL as the Primary Database
- ADR-0004 — Use Qdrant as the Vector Database
- ADR-0005 — Use LlamaIndex for RAG
- ADR-0006 — Adopt a Multi-Agent Workflow

---

# References

- System-Architecture.md
- Parser-Architecture.md
- Knowledge-Model.md
- Data-Models.md
- RAG-Architecture.md
- Workflow-Design.md

---

# Review Notes

This decision should be revisited if:

- the platform no longer supports multiple resume formats,
- parser maintenance becomes prohibitively expensive, or
- a fundamentally different document representation proves superior.

Until then, the Canonical Resume Model remains the architectural foundation of Tailr.

# ADR-0009: Adopt Prompt Versioning and Prompt Registry

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr relies on prompts for every AI capability.

Examples include:

- Resume Analysis
- Job Description Analysis
- Planning
- Retrieval
- Resume Rewriting
- Validation
- ATS Scoring

As the platform evolves, prompts will be improved continuously.

Changing prompts directly in source code creates several problems:

- Difficult rollback
- No experiment tracking
- Poor reproducibility
- Hard debugging
- No audit history
- Inconsistent agent behavior

Prompts should be treated as versioned assets rather than embedded strings.

---

# Decision

Tailr adopts a **Prompt Registry** with immutable **Prompt Versioning**.

Every prompt:

- has a unique identifier
- maintains semantic versions
- records metadata
- stores evaluation metrics
- supports rollback

Agents reference prompt IDs rather than prompt text.

---

# Decision Drivers

The prompt management system must:

- support version history
- enable experimentation
- provide reproducibility
- allow rollback
- separate prompts from code
- integrate with observability
- support A/B testing

---

# Architecture

```
Agent

↓

Prompt Registry

↓

Prompt Version

↓

Template Engine

↓

Model Provider

↓

LLM
```

Business logic never embeds prompt text.

---

# Prompt Registry

Each prompt contains:

- prompt_id
- name
- version
- owner
- description
- template
- variables
- model compatibility
- status
- created_at

Example:

```
Prompt ID:

resume_rewriter

Versions:

v1.0.0

v1.1.0

v1.2.0

v2.0.0
```

---

# Versioning Strategy

Semantic Versioning is used.

```
Major.Minor.Patch
```

Examples

```
1.0.0

1.1.0

1.1.1

2.0.0
```

### Major

Breaking prompt behavior.

### Minor

Improved reasoning.

### Patch

Grammar fixes or formatting improvements.

---

# Prompt Template

Example

```jinja
You are an expert technical resume writer.

Job Description:

{{ job_description }}

Resume:

{{ resume }}

Return only valid JSON.
```

Variables are injected during execution.

---

# Prompt Metadata

Example

```json
{
  "id": "resume_rewriter",
  "version": "1.2.0",
  "model": "qwen3:8b",
  "temperature": 0.2,
  "owner": "AI Team"
}
```

Metadata supports auditing and debugging.

---

# Prompt Storage

Prompts are stored in PostgreSQL.

Schema:

```
prompts

prompt_versions

prompt_evaluations
```

Templates are loaded dynamically.

---

# Evaluation

Every prompt version records:

- success rate
- latency
- token usage
- hallucination rate
- validation score
- ATS improvement

Poor-performing prompts are deprecated.

---

# Rollback

Example

```
v1.3.0

↓

Validation Failure

↓

Rollback

↓

v1.2.0
```

Rollback requires no code deployment.

---

# Experimentation

Prompt Registry supports:

- A/B testing
- Shadow execution
- Canary rollout
- Offline evaluation

Prompt quality improves through measurable experiments.

---

# Prompt Lifecycle

```
Draft

↓

Review

↓

Testing

↓

Evaluation

↓

Production

↓

Deprecated
```

Only production prompts are used by agents.

---

# Security

Prompt Registry enforces:

- immutable versions
- role-based access
- audit logs
- prompt signing (future)
- change history

Unauthorized prompt modification is prevented.

---

# Observability

Each inference logs:

- workflow_id
- agent
- prompt_id
- prompt_version
- model
- latency
- tokens
- validation result

Logs integrate with Langfuse and OpenTelemetry.

---

# Alternatives Considered

## Option 1 — Hardcoded Prompts

### Advantages

- Very simple
- Minimal infrastructure

### Disadvantages

- No versioning
- Difficult rollback
- Poor reproducibility
- Code deployment required

Decision: Rejected

---

## Option 2 — Files on Disk

### Advantages

- Easier maintenance
- Version controlled with Git

### Disadvantages

- Runtime updates require deployment
- Limited metadata
- No experiment tracking

Decision: Rejected

---

## Option 3 — Prompt Registry

### Advantages

- Version history
- Rollback
- Evaluation
- Dynamic loading
- Better observability
- Production-ready

### Disadvantages

- Additional database schema
- Registry management

Decision: Accepted

---

# Consequences

## Positive

- Reproducible AI behavior
- Safe experimentation
- Easy rollback
- Better debugging
- Prompt analytics
- Cleaner architecture

---

## Negative

- Additional infrastructure
- Prompt governance required
- Slight runtime lookup overhead

---

# Risks

| Risk                    | Mitigation                 |
| ----------------------- | -------------------------- |
| Prompt drift            | Immutable versions         |
| Breaking prompt changes | Semantic versioning        |
| Registry growth         | Archive deprecated prompts |
| Inconsistent variables  | Schema validation          |

---

# Architecture Integration

```
FastAPI

↓

Workflow Engine

↓

Agent

↓

Prompt Registry

↓

Model Provider

↓

LLM
```

The Prompt Registry becomes the authoritative source for all AI prompts.

---

# Related ADRs

- ADR-0005 — Use LlamaIndex as the AI Data Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0008 — Model Provider Abstraction Layer

---

# References

- LLM-Prompt-Design.md
- Observability.md
- Validation-Engine.md
- Database-Design.md

---

# Review Notes

This decision should be revisited if:

- prompts are replaced by learned policies,
- fine-tuned models eliminate prompt engineering,
- or a dedicated prompt management platform becomes the standard.

Until then, the Prompt Registry remains the authoritative source for all prompts within Tailr.

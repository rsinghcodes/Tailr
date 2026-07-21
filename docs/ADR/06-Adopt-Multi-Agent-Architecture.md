# ADR-0006: Adopt a Multi-Agent Architecture for AI Workflows

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr performs significantly more than simple text generation.

For each resume optimization request, the platform must:

- understand the job description,
- analyze the canonical resume,
- retrieve relevant professional context,
- create an optimization strategy,
- rewrite targeted sections,
- validate generated content,
- enforce AI guardrails,
- calculate ATS scores,
- generate recommendations,
- render deterministic LaTeX,
- produce the final PDF artifact.

Attempting to solve all of these tasks with a **single LLM prompt** creates several problems:

- extremely long prompts,
- poor reasoning quality,
- difficult debugging,
- limited component reuse,
- high token consumption,
- increased hallucination risk,
- weak observability,
- low maintainability.

A modular architecture is required so that each reasoning task can be optimized, tested, and monitored independently.

---

# Decision

Tailr adopts a **Multi-Agent Architecture** orchestrated by a **deterministic Workflow Engine**.

Each agent owns **one well-defined responsibility** and communicates using **structured events and typed JSON payloads**.

The Workflow Engine controls execution order, retries, state persistence, and error handling.

Agents **never invoke one another directly**.

---

# Decision Drivers

The architecture must:

- improve reasoning quality,
- reduce prompt complexity,
- encourage modularity,
- enable independent testing,
- support prompt versioning,
- reduce hallucinations,
- support guardrails,
- improve observability,
- allow parallel execution,
- support future distributed execution.

---

# High-Level Architecture

<CodeBlock language="text" content="Job Description
    │
    ▼
JD Analyzer Agent
    │
    ▼
Resume Analyzer Agent
    │
    ▼
Planning Agent
    │
    ▼
Retrieval Pipeline
    │
    ▼
Rewrite Agent
    │
    ▼
Guardrails Engine
    │
    ▼
Validation Agent
    │
    ▼
ATS Agent
    │
    ▼
Rendering Engine
    │
    ▼
PDF Artifact"/>

Each agent performs **exactly one responsibility**.

---

# Initial Agent Set

## JD Analyzer Agent

### Responsibilities

- Extract keywords
- Identify required skills
- Detect seniority
- Extract responsibilities
- Identify domain requirements
- Generate optimization targets

### Output

<CodeBlock language="json" content="{
"required_skills": ["FastAPI", "Docker", "Redis"],
"seniority": "mid",
"domain": "AI Platform",
"priority_keywords": ["RAG", "LangGraph"]
}"/>

---

## Resume Analyzer Agent

### Responsibilities

- Analyze strengths
- Detect weaknesses
- Identify missing keywords
- Understand existing skills
- Build optimization context

### Output

<CodeBlock language="json" content="{
"strengths": ["FastAPI", "Qdrant"],
"missing_keywords": ["Redis", "Docker"],
"candidate_level": "mid"
}"/>

---

## Planning Agent

### Responsibilities

- Create rewrite strategy
- Prioritize sections
- Determine optimization order
- Avoid unnecessary modifications
- Estimate expected ATS improvement

### Output

<CodeBlock language="json" content="{
"target_sections": ["summary", "projects"],
"rewrite_order": ["summary", "projects"],
"expected_ats_delta": 14
}"/>

---

## Retrieval Pipeline

### Responsibilities

- Generate semantic queries
- Retrieve relevant resume nodes
- Apply metadata filters
- Rerank results
- Assemble structured context

This stage is implemented using **LlamaIndex + Qdrant**.

---

## Rewrite Agent

### Responsibilities

- Rewrite content
- Preserve factual correctness
- Maintain writing style
- Improve ATS relevance
- Use only retrieved evidence

### Constraints

- No new employers
- No invented projects
- No fabricated metrics
- No unsupported skills

---

## Guardrails Engine

### Responsibilities

- JSON validation
- Schema validation
- Prompt injection detection
- Hallucination detection
- Resume integrity checks
- PII detection
- Output repair

### Outcomes

- **Approved**
- **Repairable**
- **Rejected**

Guardrails execute immediately after rewriting.

---

## Validation Agent

### Responsibilities

- Verify canonical schema
- Check section consistency
- Validate technology references
- Verify date consistency
- Ensure deterministic rendering compatibility

---

## ATS Agent

### Responsibilities

- Calculate ATS score
- Explain deductions
- Generate prioritized recommendations
- Compare against previous versions
- Produce detailed ATS reports

### Output

<CodeBlock language="json" content="{
"score": 87,
"keyword_coverage": 0.91,
"semantic_similarity": 0.88,
"recommendations": [
"Add Redis experience to summary"
]
}"/>

---

# Communication Model

Agents communicate only through **typed JSON events**.

Example:

<CodeBlock language="json" content="{
"event_type": "rewrite.completed",
"workflow_id": "wf_123",
"target_section": "projects",
"missing_keywords": ["Docker", "Redis"],
"priority": "high"
}"/>

This eliminates ambiguity and enables deterministic orchestration.

---

# Workflow Orchestration

The Workflow Engine executes agents in a controlled sequence.

<CodeBlock language="text" content="Receive Request
   ↓
Parse Resume
   ↓
Execute JD Analyzer
   ↓
Execute Resume Analyzer
   ↓
Execute Planner
   ↓
Execute Retrieval
   ↓
Execute Rewriter
   ↓
Execute Guardrails
   ↓
Execute Validator
   ↓
Execute ATS
   ↓
Render PDF
   ↓
Return Result"/>

Agents do not contain orchestration logic.

---

# Parallel Execution

Independent tasks may run concurrently.

<CodeBlock language="text" content="            Planner
            │
    ┌───────┴────────┐
    ▼                ▼
Resume Analysis    Retrieval Prep
    │                │
    └───────┬────────┘
            ▼
        Rewriter"/>

Parallel execution reduces end-to-end latency.

---

# Workflow State Persistence

Workflow state is persisted in PostgreSQL.

States:

- Uploaded
- Parsed
- Indexed
- Planning
- Retrieval
- Rewrite
- Guardrails
- Validation
- ATS
- Rendering
- Completed
- Failed

State transitions are append-only and auditable.

---

# Failure Handling

If an agent fails:

- retry with exponential backoff,
- record structured error details,
- stop dependent stages,
- preserve workflow state,
- allow manual replay,
- emit telemetry events.

Example retry policy:

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Error Type</Table.Cell><Table.Cell align="end">Retries</Table.Cell></Table.Row><Table.Row><Table.Cell>LLM timeout</Table.Cell><Table.Cell align="end">3</Table.Cell></Table.Row><Table.Row><Table.Cell>Rate limit</Table.Cell><Table.Cell align="end">5</Table.Cell></Table.Row><Table.Row><Table.Cell>Qdrant unavailable</Table.Cell><Table.Cell align="end">3</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrail rejection</Table.Cell><Table.Cell align="end">0</Table.Cell></Table.Row></Table>

Partial failures must never corrupt user data.

---

# Prompt Isolation

Every agent owns:

- system prompt,
- output schema,
- temperature,
- model configuration,
- token budget,
- evaluation metrics,
- fallback model policy.

Prompt isolation prevents unintended interactions between responsibilities.

---

# Human Approval Gate

High-impact changes require explicit approval.

Examples:

- summary rewrite,
- experience reordering,
- project promotion,
- removal of content,
- major ATS-driven restructuring.

The workflow pauses until the user approves or rejects the proposed changes.

---

# Evaluation Strategy

Each agent is evaluated independently.

Metrics include:

- success rate,
- latency,
- token usage,
- schema validity,
- hallucination rate,
- guardrail pass rate,
- ATS improvement,
- retrieval precision,
- retry frequency.

This enables targeted optimization without affecting unrelated agents.

---

# Observability

Every execution records:

- workflow ID,
- agent name,
- prompt version,
- model provider,
- token counts,
- latency,
- estimated cost,
- validation status,
- guardrail outcome,
- retry count,
- correlation ID.

Telemetry is exported through **OpenTelemetry** and stored for evaluation and debugging.

---

# LLM Provider Abstraction

Agents do not call providers directly.

<CodeBlock language="text" content="Agent
↓
LLM Provider Interface
↓
Router
├── Ollama
├── OpenAI
├── Anthropic
└── Gemini"/>

This allows model replacement without changing agent logic.

---

# Future Distributed Execution

The architecture is designed to evolve into independently scalable services.

<CodeBlock language="text" content="API Gateway
  │
  ▼
Workflow Service
  │
┌───┼───────────┐
▼   ▼           ▼
JD  Rewrite   Validation
Svc   Svc        Svc"/>

Because agents communicate through structured events, they can be moved to separate processes or services with minimal changes.

---

# Alternatives Considered

## Option 1 — Single Prompt

### Advantages

- Simple implementation
- Few components

### Disadvantages

- Huge prompts
- Difficult debugging
- High hallucination risk
- Poor reuse
- Weak observability

**Decision:** Rejected

---

## Option 2 — Sequential Prompt Chain

### Advantages

- Better than a single prompt
- Sequential reasoning

### Disadvantages

- Weak separation of concerns
- Difficult evaluation
- Hard to parallelize
- Shared prompt state causes drift

**Decision:** Rejected

---

## Option 3 — Multi-Agent Architecture

### Advantages

- Modular
- Testable
- Reusable
- Observable
- Easier prompt engineering
- Lower hallucination rates
- Supports future expansion
- Enables distributed execution

### Disadvantages

- Additional orchestration layer
- More prompts to manage
- More telemetry to collect
- Higher initial complexity

**Decision:** Accepted

---

# Consequences

## Positive

- Better reasoning quality
- Smaller prompts
- Independent agent testing
- Easier debugging
- Prompt versioning
- Lower hallucination rates
- Better observability
- Parallel execution support
- Easier future scaling

---

## Negative

- Additional orchestration logic
- More configuration files
- More telemetry storage
- Slightly higher latency overhead per stage

---

# Risks

| Risk                        | Mitigation                                       |
| --------------------------- | ------------------------------------------------ |
| Agent coordination failures | Central deterministic workflow engine            |
| Prompt drift                | Prompt versioning and evaluation                 |
| Increased latency           | Parallelize independent stages                   |
| Context inconsistency       | Canonical Resume Model as shared source of truth |
| Event schema changes        | Versioned event contracts                        |
| Guardrail bypass            | Mandatory guardrail stage before validation      |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
LangGraph Workflow Engine
│
▼
Multi-Agent Layer
│
├── LlamaIndex (RAG & Retrieval)
│       │
│       ▼
│   Qdrant Cloud
│
▼
LLM Provider
│
▼
Guardrails
│
▼
Validation
│
▼
Rendering Engine
│
▼
PDF Artifact"/>

The **Multi-Agent Layer is responsible for AI reasoning**, while **business orchestration remains deterministic**.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture with Hexagonal Boundaries
- ADR-0003 — Use FastAPI as the Primary Backend Framework
- ADR-0004 — Use PostgreSQL as the Primary Transactional Database
- ADR-0005 — Use LlamaIndex as the RAG and Knowledge Framework
- ADR-0007 — Event-Driven Workflow Engine (LangGraph)
- ADR-0008 — Adopt a Validation & Guardrails Engine

---

# References

- agent-architecture.md
- workflow-design.md
- rag-architecture.md
- validation-engine.md
- testing.md
- guardrails-architecture.md
- evaluation-architecture.md

---

# Review Notes

This decision should be revisited if:

- orchestration latency becomes unacceptable,
- workflow complexity exceeds operational benefits,
- a simpler orchestration model proves sufficient,
- or distributed execution introduces excessive operational overhead.

Until then, the **Multi-Agent Architecture remains the standard approach for AI workflow execution within Tailr**, with deterministic orchestration, structured communication, mandatory guardrails, and independently testable AI agents.

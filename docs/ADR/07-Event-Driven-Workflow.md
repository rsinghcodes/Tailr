# ADR-0007: Adopt an Event-Driven Workflow Engine for AI Agent Orchestration

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr executes multiple AI agents during resume optimization.

Current workflow stages include:

- Resume Parsing
- Knowledge Indexing
- JD Analysis
- Resume Analysis
- Planning
- Retrieval
- Rewriting
- Guardrails
- Validation
- ATS Scoring
- PDF Rendering

Future capabilities will include:

- Cover Letter Generation
- LinkedIn Optimization
- Portfolio Analysis
- Interview Preparation
- Career Gap Analysis
- Skill Gap Analysis
- Personalized Learning Recommendations

A simple sequential implementation would tightly couple agents and make the workflow difficult to extend, debug, and recover.

As the number of AI capabilities grows, orchestration complexity increases rapidly.

The platform therefore requires a dedicated workflow engine that provides deterministic orchestration, state persistence, retries, checkpointing, and observability.

---

# Decision

Tailr adopts an **Event-Driven Workflow Engine** based on **LangGraph** with persistent workflow state stored in PostgreSQL.

The Workflow Engine is responsible for:

- workflow lifecycle management,
- agent scheduling,
- event routing,
- retries,
- checkpointing,
- state persistence,
- failure recovery,
- workflow replay,
- timeout handling,
- observability and tracing.

Agents perform isolated units of work.

The Workflow Engine decides **when**, **why**, and **under what conditions** they run.

---

# Decision Drivers

The orchestration layer must:

- decouple agents,
- support retries,
- enable checkpoint recovery,
- support workflow replay,
- improve observability,
- support future parallel execution,
- simplify testing,
- support human approval gates,
- enable distributed execution in the future,
- keep orchestration deterministic.

---

# Workflow Architecture

<CodeBlock language="text" content="                API Request
                  │
                  ▼
         Workflow Engine
                  │
   ┌──────────────┼──────────────┐
   ▼              ▼              ▼
Event Router   Workflow State   Scheduler
   │
   ▼
Agent Execution
   │
   ▼
Guardrails Engine
   │
   ▼
Validation Engine"/>

The Workflow Engine is the **single coordinator** for all AI execution.

---

# Execution Flow

<CodeBlock language="text" content="Workflow Started
     ↓
Resume Uploaded
     ↓
Resume Parsed
     ↓
Knowledge Indexed
     ↓
JD Analysis Completed
     ↓
Resume Analysis Completed
     ↓
Planning Completed
     ↓
Retrieval Completed
     ↓
Rewrite Completed
     ↓
Guardrails Passed
     ↓
Validation Passed
     ↓
ATS Generated
     ↓
PDF Generated
     ↓
Workflow Completed"/>

Every stage emits a structured event.

---

# Workflow State Machine

Tailr uses an explicit workflow state machine.

<CodeBlock language="text" content="Uploaded → Parsed → Indexed → Planning
→ Retrieval → Rewrite → Guardrails
→ Validation → ATS → Rendering
→ Completed

Any state → Failed
Validation → AwaitingApproval
AwaitingApproval → ResumeExecution"/>

State transitions are validated before persistence.

---

# Persisted Workflow State

Each workflow stores:

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Field</Table.Cell><Table.Cell>Description</Table.Cell></Table.Row><Table.Row><Table.Cell>workflow_id</Table.Cell><Table.Cell>Unique workflow identifier</Table.Cell></Table.Row><Table.Row><Table.Cell>user_id</Table.Cell><Table.Cell>Workflow owner</Table.Cell></Table.Row><Table.Row><Table.Cell>resume_version_id</Table.Cell><Table.Cell>Source resume version</Table.Cell></Table.Row><Table.Row><Table.Cell>current_state</Table.Cell><Table.Cell>Current workflow state</Table.Cell></Table.Row><Table.Row><Table.Cell>status</Table.Cell><Table.Cell>Running / Completed / Failed</Table.Cell></Table.Row><Table.Row><Table.Cell>retry_count</Table.Cell><Table.Cell>Total retry attempts</Table.Cell></Table.Row><Table.Row><Table.Cell>started_at</Table.Cell><Table.Cell>Workflow start time</Table.Cell></Table.Row><Table.Row><Table.Cell>updated_at</Table.Cell><Table.Cell>Last update time</Table.Cell></Table.Row><Table.Row><Table.Cell>completed_at</Table.Cell><Table.Cell>Completion time</Table.Cell></Table.Row><Table.Row><Table.Cell>trace_id</Table.Cell><Table.Cell>Distributed tracing correlation ID</Table.Cell></Table.Row></Table>

State is persisted in **PostgreSQL** using atomic transactions.

---

# Event Model

Events are immutable and versioned.

Example:

<CodeBlock language="json" content="{
"event_type": "resume.parsed",
"event_version": 1,
"workflow_id": "wf_123",
"timestamp": "2026-07-20T10:15:30Z",
"payload": {
"resume_version_id": "rv_456",
"sections": ["summary", "projects", "experience"]
}
}"/>

Events are append-only and never mutated after publication.

---

# Typed Workflow Events

LangGraph workflow events are represented as typed objects.

<CodeBlock language="python" content="class ResumeParsedEvent(Event):
workflow_id: str
resume_version_id: str
sections: list[str]

class RewriteCompletedEvent(Event):
workflow_id: str
rewritten_sections: list[str]
token_usage: int"/>

Typed events provide:

- compile-time validation,
- better IDE support,
- safer refactoring,
- deterministic contracts.

---

# Agent Execution Contract

Workflow Engine execution:

<CodeBlock language="text" content="Receive Event
   ↓
Resolve Agent
   ↓
Execute Agent
   ↓
Run Guardrails
   ↓
Validate Output
   ↓
Persist Checkpoint
   ↓
Publish Next Event"/>

Agents never invoke other agents directly.

---

# Retry Strategy

Retries use **exponential backoff with jitter**.

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Failure Type</Table.Cell><Table.Cell align="end">Max Retries</Table.Cell></Table.Row><Table.Row><Table.Cell>LLM timeout</Table.Cell><Table.Cell align="end">3</Table.Cell></Table.Row><Table.Row><Table.Cell>Rate limit</Table.Cell><Table.Cell align="end">5</Table.Cell></Table.Row><Table.Row><Table.Cell>Qdrant timeout</Table.Cell><Table.Cell align="end">3</Table.Cell></Table.Row><Table.Row><Table.Cell>Network error</Table.Cell><Table.Cell align="end">5</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrail rejection</Table.Cell><Table.Cell align="end">0</Table.Cell></Table.Row><Table.Row><Table.Cell>Validation failure</Table.Cell><Table.Cell align="end">0</Table.Cell></Table.Row></Table>

Retries are configurable per workflow stage.

---

# Checkpointing

A checkpoint is written after every successful stage.

Example:

<CodeBlock language="text" content="Resume Parsed        ✓
Knowledge Indexed    ✓
Planner Completed    ✓
Retriever Completed  ✓
Rewrite Completed    ✗"/>

On recovery, execution resumes from the **last successful checkpoint** rather than restarting the entire workflow.

---

# Idempotency

Every event includes an idempotency key.

<CodeBlock language="json" content="{
"workflow_id": "wf_123",
"event_id": "evt_789",
"idempotency_key": "wf_123:rewrite:1"
}"/>

Duplicate events are ignored safely.

---

# Parallel Execution

Independent stages may execute concurrently.

<CodeBlock language="text" content="                Resume
                │
      ┌─────────┴─────────┐
      ▼                   ▼
Resume Analyzer       JD Analyzer
      │                   │
      └─────────┬─────────┘
                ▼
             Planner"/>

Parallel execution reduces total workflow latency and improves throughput.

---

# Human Approval Gates

Certain operations require explicit user approval.

Examples:

- major summary rewrite,
- experience reordering,
- project promotion,
- removal of content,
- significant ATS-driven restructuring.

The workflow transitions to **AwaitingApproval** and pauses until a decision is received.

---

# Timeout Handling

Each stage has a maximum execution time.

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Stage</Table.Cell><Table.Cell align="end">Timeout</Table.Cell></Table.Row><Table.Row><Table.Cell>JD Analysis</Table.Cell><Table.Cell align="end">30s</Table.Cell></Table.Row><Table.Row><Table.Cell>Retrieval</Table.Cell><Table.Cell align="end">15s</Table.Cell></Table.Row><Table.Row><Table.Cell>Rewrite</Table.Cell><Table.Cell align="end">90s</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrails</Table.Cell><Table.Cell align="end">10s</Table.Cell></Table.Row><Table.Row><Table.Cell>Validation</Table.Cell><Table.Cell align="end">15s</Table.Cell></Table.Row><Table.Row><Table.Cell>PDF Rendering</Table.Cell><Table.Cell align="end">60s</Table.Cell></Table.Row></Table>

Timed-out stages are marked failed and follow the retry policy.

---

# Observability

Every workflow records:

- workflow ID,
- trace ID,
- event sequence,
- current state,
- execution latency,
- token usage,
- prompt version,
- model provider,
- retry count,
- guardrail outcomes,
- validation status,
- estimated cost.

Telemetry is exported through **OpenTelemetry** and correlated across all workflow stages.

---

# Workflow Replay

A failed workflow can be replayed from any checkpoint.

Replay modes:

- **Full replay** — restart from the beginning
- **Stage replay** — rerun a single stage
- **Forward replay** — continue from the last successful checkpoint

Replay is essential for debugging and regression testing.

---

# Failure Recovery

Recoverable failures include:

- Ollama unavailable,
- Qdrant timeout,
- embedding generation failure,
- PDF renderer failure,
- temporary network failures,
- rate limiting.

Because workflow state is persisted, completed stages are not repeated unnecessarily.

---

# Alternatives Considered

## Option 1 — Sequential Function Calls

### Advantages

- Very simple
- Easy to understand

### Disadvantages

- Tight coupling
- No checkpoints
- No replay support
- Difficult debugging
- Poor scalability

**Decision:** Rejected

---

## Option 2 — Agents Calling Other Agents

### Advantages

- Modular implementation

### Disadvantages

- Hidden execution flow
- Circular dependencies
- Difficult testing
- Poor observability
- Retry logic becomes fragmented

**Decision:** Rejected

---

## Option 3 — Event-Driven Workflow Engine

### Advantages

- Decoupled architecture
- Checkpoint recovery
- Workflow replay
- Parallel execution
- Strong observability
- Deterministic orchestration
- Easier testing
- Future distributed execution

### Disadvantages

- Additional orchestration complexity
- More persisted state
- Requires event schema management

**Decision:** Accepted

---

# Consequences

## Positive

- Modular workflows
- Easier debugging
- Reliable retries
- Checkpoint recovery
- Workflow replay
- Parallel execution
- Better observability
- Reusable orchestration logic
- Easier future scaling

---

## Negative

- Additional infrastructure complexity
- More database writes
- Event schema versioning overhead
- More telemetry data to manage

---

# Risks

| Risk                      | Mitigation                   |
| ------------------------- | ---------------------------- |
| Workflow state corruption | Atomic database transactions |
| Event duplication         | Idempotent event handlers    |
| Infinite retries          | Maximum retry policies       |
| Long-running workflows    | Timeouts and cancellation    |
| Schema evolution          | Versioned event contracts    |
| Replay inconsistencies    | Immutable checkpoints        |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
Workflow Engine
│
▼
Multi-Agent Layer
│
▼
LangGraph
│
▼
Qdrant Cloud
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
Generated Resume"/>

The Workflow Engine orchestrates execution while agents remain **stateless and deterministic**.

---

# Future Enhancements

Planned enhancements include:

- conditional branching,
- dynamic workflow graphs,
- scheduled workflows,
- workflow templates,
- multi-worker execution,
- Redis/Kafka event bus,
- distributed workflow execution,
- cross-workflow dependencies,
- human-in-the-loop review queues.

The current architecture is intentionally designed so these capabilities can be added incrementally.

---

# Related ADRs

- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture with Hexagonal Boundaries
- ADR-0005 — LlamaIndex as the RAG and Knowledge Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0008 — Validation & Guardrails Engine

---

# References

- workflow-design.md
- agent-architecture.md
- observability.md
- testing.md
- deployment.md
- guardrails-architecture.md

---

# Review Notes

This decision should be revisited if:

- workflow overhead outweighs orchestration benefits,
- an external workflow platform becomes strategically preferable,
- distributed execution requirements fundamentally change,
- or workflow complexity is significantly reduced.

Until then, the **Event-Driven Workflow Engine remains the standard orchestration mechanism for Tailr**, providing deterministic execution, persistent state, replay capability, mandatory guardrails, and observable AI workflow orchestration.

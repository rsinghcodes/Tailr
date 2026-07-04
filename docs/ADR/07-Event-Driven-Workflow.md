# ADR-0007: Adopt an Event-Driven Workflow Engine for AI Agent Orchestration

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr executes multiple AI agents during resume optimization.

Examples include:

- JD Analyzer
- Resume Analyzer
- Planner
- Retriever
- Rewriter
- Validator
- ATS Scorer

A simple sequential implementation tightly couples agents and makes the workflow difficult to extend.

As additional capabilities such as Cover Letter Generation, LinkedIn Optimization, Portfolio Analysis, and Interview Preparation are introduced, orchestration complexity grows rapidly.

The platform therefore requires a dedicated workflow engine.

---

# Decision

Tailr adopts an **Event-Driven Workflow Engine**.

The Workflow Engine owns:

- workflow lifecycle
- agent scheduling
- retries
- checkpoints
- event publishing
- workflow state
- failure recovery
- observability

Agents perform work.

The Workflow Engine decides **when** they run.

---

# Decision Drivers

The orchestration layer must:

- decouple agents
- support retries
- enable checkpoint recovery
- improve observability
- support future parallel execution
- simplify testing
- enable workflow replay

---

# Workflow Architecture

```
               API Request
                     │
                     ▼
            Workflow Engine
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
Event Bus      Workflow State     Scheduler
      │
      ▼
Agent Execution
```

The Workflow Engine becomes the single coordinator.

---

# Execution Flow

```
Workflow Started

↓

Resume Uploaded

↓

Resume Parsed

↓

Knowledge Built

↓

JD Analysis Completed

↓

Planning Completed

↓

Retrieval Completed

↓

Rewrite Completed

↓

Validation Passed

↓

ATS Generated

↓

PDF Generated

↓

Workflow Completed
```

Every stage emits an event.

---

# Workflow State

Each workflow stores:

```
workflow_id

user_id

resume_version

current_step

status

started_at

completed_at

retry_count
```

State is persisted in PostgreSQL.

---

# Event Model

Example event:

```json
{
  "event": "resume.parsed",
  "workflow_id": "wf_123",
  "timestamp": "...",
  "status": "completed"
}
```

Events are immutable.

---

# Agent Execution

Workflow Engine:

```
Publish Event

↓

Resolve Agent

↓

Execute Agent

↓

Validate Output

↓

Persist State

↓

Publish Next Event
```

Agents never invoke each other directly.

---

# Retry Strategy

Failures are retried using exponential backoff.

Example:

Attempt 1

↓

Attempt 2

↓

Attempt 3

↓

Workflow Failed

Retries are configurable per agent.

---

# Checkpointing

Workflow checkpoints are stored after each successful step.

Example

```
Resume Parsed ✓

Knowledge Built ✓

Planner ✓

Retriever ✓

Rewriter ❌
```

Execution resumes from the failed step instead of restarting the workflow.

---

# Parallel Execution

Independent agents may execute concurrently.

Example

```
              Resume
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
Resume Analyzer     JD Analyzer
       │                   │
       └─────────┬─────────┘
                 ▼
              Planner
```

Parallel execution reduces total workflow latency.

---

# Observability

Each workflow records:

- workflow_id
- trace_id
- event sequence
- execution time
- token usage
- prompt version
- agent status

Events integrate with OpenTelemetry and Langfuse.

---

# Failure Recovery

Recoverable failures include:

- Ollama unavailable
- Qdrant timeout
- embedding failure
- renderer failure

Workflow state enables recovery without repeating completed work.

---

# Alternatives Considered

## Option 1 — Sequential Function Calls

### Advantages

- Very simple
- Easy to understand

### Disadvantages

- Tight coupling
- No checkpoints
- Poor scalability
- Difficult debugging

Decision: Rejected

---

## Option 2 — Agents Calling Other Agents

### Advantages

- Modular implementation

### Disadvantages

- Circular dependencies
- Hidden execution flow
- Difficult testing
- Hard to observe

Decision: Rejected

---

## Option 3 — Event-Driven Workflow Engine

### Advantages

- Decoupled architecture
- Checkpoint recovery
- Parallel execution
- Easy observability
- Workflow replay
- Scalable orchestration

### Disadvantages

- More implementation effort
- Additional workflow state management

Decision: Accepted

---

# Consequences

## Positive

- Modular workflows
- Better debugging
- Easier retries
- Future parallelism
- Improved observability
- Reusable orchestration

---

## Negative

- Additional infrastructure
- More persisted state
- Workflow management complexity

---

# Risks

| Risk                      | Mitigation                       |
| ------------------------- | -------------------------------- |
| Workflow state corruption | Atomic database transactions     |
| Event duplication         | Idempotent event handlers        |
| Infinite retries          | Maximum retry policy             |
| Long-running workflows    | Timeout and cancellation support |

---

# Architecture Integration

```
FastAPI

↓

Workflow Engine

↓

Multi-Agent Layer

↓

LlamaIndex

↓

Qdrant

↓

Ollama

↓

Generated Resume
```

The Workflow Engine orchestrates execution while agents remain stateless.

---

# Future Enhancements

Future versions may introduce:

- Human approval steps
- Workflow branching
- Conditional execution
- Scheduled workflows
- Workflow templates
- Distributed execution
- Message queue integration
- Multi-worker execution

---

# Related ADRs

- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture
- ADR-0005 — LlamaIndex
- ADR-0006 — Multi-Agent Architecture

---

# References

- Workflow-Design.md
- Agent-Architecture.md
- Observability.md
- Testing.md
- Deployment.md

---

# Review Notes

This decision should be revisited if:

- workflows become simple enough that orchestration overhead outweighs benefits,
- the platform adopts an external workflow orchestration system,
- or distributed execution requirements fundamentally change.

Until then, the Event-Driven Workflow Engine remains the standard orchestration mechanism for Tailr.

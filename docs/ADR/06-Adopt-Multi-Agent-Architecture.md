# ADR-0006: Adopt a Multi-Agent Architecture for AI Workflows

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr performs more than simple text generation.

For each resume optimization request, the platform must:

- Understand the job description
- Analyze the resume
- Retrieve relevant context
- Plan improvements
- Rewrite sections
- Validate generated content
- Calculate ATS scores
- Produce the final LaTeX resume

Attempting to solve all of these tasks with a single prompt creates several problems:

- Extremely long prompts
- Poor reasoning quality
- Difficult debugging
- Limited reuse
- High token usage
- High hallucination rate
- Low maintainability

A more modular approach is required.

---

# Decision

Tailr adopts a **Multi-Agent Architecture**.

Each AI agent owns one well-defined responsibility.

Agents communicate through structured data rather than natural language.

Business orchestration remains deterministic and is controlled by the Workflow Engine.

---

# Decision Drivers

The architecture should:

- Improve reasoning quality
- Reduce prompt complexity
- Encourage modularity
- Enable independent testing
- Support prompt versioning
- Reduce hallucinations
- Allow future agent expansion
- Improve observability

---

# Agent Architecture

```
                 Job Description
                        │
                        ▼
                JD Analyzer Agent
                        │
                        ▼
                Resume Analysis Agent
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
               Validation Agent
                        │
                        ▼
                ATS Scoring Agent
                        │
                        ▼
                  PDF Renderer
```

Each agent performs exactly one responsibility.

---

# Initial Agents

## JD Analyzer

Responsibilities

- Extract keywords
- Identify required skills
- Identify seniority
- Detect responsibilities
- Generate optimization targets

---

## Resume Analysis Agent

Responsibilities

- Analyze strengths
- Detect weaknesses
- Identify missing experience
- Understand existing skills
- Build optimization context

---

## Planning Agent

Responsibilities

- Create rewrite strategy
- Prioritize sections
- Determine optimization order
- Avoid unnecessary modifications

---

## Rewrite Agent

Responsibilities

- Rewrite content
- Preserve factual correctness
- Maintain writing style
- Improve ATS relevance

---

## Validation Agent

Responsibilities

- Verify schema
- Detect hallucinations
- Validate technologies
- Check formatting
- Verify consistency

---

## ATS Agent

Responsibilities

- Score resume
- Explain deductions
- Generate recommendations
- Compare versions

---

# Communication Model

Agents never communicate through free-form text.

Instead they exchange structured JSON.

Example

```json
{
  "target_section": "projects",
  "missing_keywords": ["Docker", "Redis"],
  "priority": "high"
}
```

Structured communication improves reliability.

---

# Workflow Orchestration

The Workflow Engine coordinates execution.

```
Receive Request

↓

Execute JD Analyzer

↓

Execute Resume Analysis

↓

Execute Planner

↓

Execute Retrieval

↓

Execute Rewriter

↓

Execute Validator

↓

Execute ATS

↓

Return Result
```

Agents do not invoke one another directly.

---

# Failure Handling

If an agent fails:

- Retry with exponential backoff
- Log execution details
- Return structured error
- Stop dependent agents
- Preserve workflow state

Partial failures never corrupt user data.

---

# Prompt Isolation

Every agent owns:

- System prompt
- Output schema
- Temperature
- Model configuration
- Evaluation metrics

Prompt isolation prevents unintended interactions between responsibilities.

---

# Evaluation Strategy

Each agent is evaluated independently.

Metrics include:

- Success rate
- Latency
- Token usage
- Schema validity
- Hallucination rate
- Validation pass rate

This enables targeted optimization.

---

# Observability

Every execution records:

- Workflow ID
- Agent name
- Prompt version
- Model
- Tokens
- Latency
- Cost
- Validation status

Agent telemetry integrates with Langfuse and OpenTelemetry.

---

# Alternatives Considered

## Option 1 — Single Prompt

### Advantages

- Simple implementation
- Fewer components

### Disadvantages

- Large prompts
- Difficult debugging
- High hallucination risk
- Limited reuse

Decision: Rejected

---

## Option 2 — Chain of Prompts

### Advantages

- Better than a single prompt
- Sequential reasoning

### Disadvantages

- Weak separation of concerns
- Limited scalability
- Difficult evaluation

Decision: Rejected

---

## Option 3 — Multi-Agent Architecture

### Advantages

- Modular
- Testable
- Reusable
- Observable
- Easier prompt engineering
- Supports future expansion

### Disadvantages

- More orchestration logic
- Increased implementation complexity

Decision: Accepted

---

# Consequences

## Positive

- Better reasoning quality
- Smaller prompts
- Independent agent testing
- Easier debugging
- Prompt versioning
- Lower hallucination rates
- Improved maintainability

---

## Negative

- Additional orchestration layer
- More prompts to manage
- More telemetry to collect

---

# Risks

| Risk                        | Mitigation                                       |
| --------------------------- | ------------------------------------------------ |
| Agent coordination failures | Central workflow orchestration                   |
| Prompt drift                | Prompt versioning                                |
| Increased latency           | Parallelize independent agents                   |
| Context inconsistency       | Canonical Resume Model as shared source of truth |

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

Response
```

The Multi-Agent Layer is responsible for AI reasoning, while business orchestration remains deterministic.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture
- ADR-0003 — Use FastAPI as the Primary Backend Framework
- ADR-0004 — Use PostgreSQL as the Primary Database
- ADR-0005 — Use LlamaIndex as the AI Data Framework

---

# References

- Agent-Architecture.md
- Workflow-Design.md
- RAG-Architecture.md
- Validation-Engine.md
- Testing.md

---

# Review Notes

This decision should be revisited if:

- agent orchestration introduces unacceptable latency,
- workflow complexity significantly exceeds operational benefits,
- or a simpler orchestration model proves sufficient.

Until then, the Multi-Agent Architecture remains the standard approach for AI workflow execution within Tailr.

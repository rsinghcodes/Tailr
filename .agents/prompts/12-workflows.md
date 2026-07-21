# LangGraph Workflows — Production Implementation Prompt

## Objective

Implement the complete production-ready **Workflow Orchestration Module** for Tailr.

This module coordinates the entire resume optimization pipeline using an event-driven, state-machine workflow built on **LangGraph**.

The Workflow Module is responsible for:

- graph state management,
- workflow node orchestration,
- guardrails integration at every generation step,
- retry strategy with policy-defined backoff,
- state persistence and checkpointing,
- streaming progress updates,
- distributed tracing,
- human-in-the-loop approval,
- workflow events,
- cancellation support,
- and failure isolation.

Only workflows orchestrate agents. Individual agents never orchestrate other agents.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/ai-agents.md
- rules/testing.md
- rules/logging.md
- ADR-0002 — Clean Architecture
- ADR-0006 — Adopt Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0011 — Validation & Guardrails Engine
- 06-Workflow-Design.md
- 02-Agent-Architecture.md
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Architecture Constraints

## Guardrails Placement

Guardrails is not a one-time gate at the end of the workflow — it runs after **every** generation or rewrite step, since each step produces new AI output that must be independently checked.

A workflow node may only transition forward if the preceding Guardrails check returned `approved` or `repaired`.

A `rejected` result transitions the workflow to retry or to a terminal `Failed` state with a structured error.

---

# Workflow State

Every step receives and produces the shared workflow state.

```python
WorkflowState(
    request_id: str,
    workflow_id: str,
    user_id: str,
    resume: Resume,
    job_description: JobDescription,
    resume_model: Resume | None,
    job_requirements: JobRequirements | None,
    retrieved_chunks: list[RetrievalResult] | None,
    rewrite_plan: PlanningOutput | None,
    rewritten_resume: Resume | None,
    guardrail_report: GuardrailResult | None,
    validation_report: ValidationResult | None,
    ats_report: ATSAnalysisOutput | None,
    critic_report: CriticOutput | None,
    render_result: RenderResult | None,
    status: WorkflowStatus,
    current_step: str,
    retry_count: int,
    errors: list[WorkflowError],
    telemetry: WorkflowTelemetry,
    step_history: list[StepRecord],
    created_at: datetime,
    updated_at: datetime,
)
```

---

# Workflow States

```text
NEW → PARSING → INDEXING → JD_ANALYSIS → RETRIEVAL → PLANNING
→ REWRITING → GUARDRAILS → VALIDATING → ATS_ANALYSIS
→ AWAITING_APPROVAL → RENDERING → COMPILING → COMPLETED
```

Failure transitions: any state → `FAILED`

Cancellation transitions: any state → `CANCELLED`

---

# Workflow Nodes

Implement the following nodes in the LangGraph graph.

---

## Parse Resume Node

- invoke parser (software, no LLM)
- produce Canonical Resume Model
- emit `ResumeParsed` event
- transition to `INDEXING`

---

## Build Knowledge Index Node

- create semantic chunks
- generate embeddings
- store in vector database
- emit `KnowledgeIndexed` event
- transition to `JD_ANALYSIS`

---

## Analyze Job Description Node

- invoke JD Analyzer agent
- run Guardrails (`analysis_standard` profile)
- if approved → persist `JobRequirements`, transition to `RETRIEVAL`
- if rejected → retry or fail

---

## Retrieve Context Node

- invoke hybrid retriever
- rerank results
- scan for prompt injection (Guardrails injection scan)
- assemble context package
- emit `RetrievalCompleted` event
- transition to `PLANNING`

---

## Planning Node

- invoke Planning agent
- run Guardrails (`analysis_standard` profile)
- if approved → persist `RewritePlan`, transition to `REWRITING`
- if rejected → retry or fail

---

## Rewrite Node

- invoke Rewrite agent
- run Guardrails (`rewrite_strict` profile)
- if approved → transition to `VALIDATING`
- if repaired → transition to `VALIDATING`
- if rejected → retry or fail

---

## Guardrails Node

Reusable guardrail execution node. Invoked after every generation step.

### Input

- AI-generated content
- guardrail profile name
- canonical resume model (for hallucination comparison)

### Output

- `GuardrailResult` with status, violations, repairs

### Behavior

- `approved` → continue
- `repaired` → continue with repaired content
- `rejected` → retry (if retries remain) or transition to `FAILED`

---

## Validation Node

- invoke business validators (runs only after Guardrails has approved)
- check date consistency, company consistency, formatting rules
- emit `ValidationCompleted` event
- if passed → transition to `ATS_ANALYSIS`
- if failed → retry rewrite

---

## ATS Analysis Node

- invoke ATS Advisor agent
- run Guardrails (`analysis_standard` profile)
- emit `ATSGenerated` event
- transition to `AWAITING_APPROVAL`

---

## Human Approval Node

- pause workflow and await user decision
- user can: approve, reject, regenerate section, manual edit, request different tone
- approval is mandatory before rendering
- approvals are auditable (reviewer, timestamp)
- emit `ResumeApproved` event
- transition to `RENDERING`

---

## Render Node

- convert Resume Model to LaTeX (deterministic, no LLM)
- template-driven rendering
- emit `RenderingCompleted` event
- transition to `COMPILING`

---

## Compile Node

- compile LaTeX to PDF
- capture compilation logs
- detect LaTeX errors
- verify PDF generation
- compute checksum
- emit `CompilationCompleted` event
- transition to `COMPLETED`

---

## Store Version Node

- create new resume version
- persist workflow artifacts
- persist guardrail audit trail
- all in same transaction

---

# Retry Strategy

- configurable retry attempts per node (default: 3)
- exponential backoff with configurable base
- retry only the failed step, not the entire workflow
- guardrail rejections count toward retry budget
- max retries exhausted → terminal `FAILED` state with structured error

---

# State Persistence & Checkpointing

- persist workflow state after each successful step
- support resume-from-checkpoint after failure
- checkpoint includes full state + telemetry
- use database for durable persistence

---

# Streaming

- emit progress events for frontend consumption
- include: workflow_id, status, progress %, current_step, estimated_seconds_remaining
- use Server-Sent Events or WebSocket

---

# Workflow Events

Emit structured events at each step:

- `WorkflowStarted`
- `ResumeParsed`
- `KnowledgeIndexed`
- `JDAnalyzed`
- `RetrievalCompleted`
- `PlanningCompleted`
- `RewriteCompleted`
- `GuardrailsCompleted`
- `ValidationCompleted`
- `ATSGenerated`
- `ResumeApproved`
- `RenderingCompleted`
- `CompilationCompleted`
- `WorkflowCompleted`
- `WorkflowFailed`
- `WorkflowCancelled`
- `WorkflowRetried`

Each event includes: event_id, workflow_id, timestamp, step, metadata.

---

# Cancellation

- any running workflow can be cancelled
- cancellation cleans up resources
- cancelled state is terminal
- emit `WorkflowCancelled` event

---

# Telemetry

Every workflow emits:

- workflow_id, workflow_name
- current_state, state transitions
- per-step duration, retry_count
- total token_usage
- model_versions, prompt_versions
- guardrail outcomes per step
- total workflow duration

Carry the same trace ID across all Guardrails invocations within the workflow.

---

# Required File Structure

```text
workflows/
├── __init__.py
├── graph.py
├── state.py
├── nodes/
│   ├── __init__.py
│   ├── parse.py
│   ├── index.py
│   ├── analyze_jd.py
│   ├── retrieve.py
│   ├── plan.py
│   ├── rewrite.py
│   ├── guardrails.py
│   ├── validate.py
│   ├── ats_analysis.py
│   ├── human_approval.py
│   ├── render.py
│   ├── compile.py
│   └── store_version.py
├── events/
│   ├── __init__.py
│   └── workflow_events.py
├── retry/
│   ├── __init__.py
│   └── strategy.py
├── streaming/
│   ├── __init__.py
│   └── progress.py
├── persistence/
│   ├── __init__.py
│   └── checkpoint.py
├── exceptions.py
└── telemetry.py
```

---

# Testing Requirements

Generate tests for:

- full workflow execution (happy path),
- individual node execution,
- guardrail approved/repaired/rejected at each generation step,
- retry behavior (success after retry, exhausted retries),
- state transitions (valid and invalid),
- checkpoint persistence and recovery,
- cancellation,
- streaming progress events,
- workflow event emission,
- human approval flow,
- telemetry emission,
- adversarial tests (injection in retrieved context, hallucinated rewrite),
- and timeout handling.

Use: pytest, pytest-asyncio, mock agents and providers.

Target coverage: **90%+**.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- be async-first,
- support horizontal scaling,
- and be production deployable.

---

# Output Requirements

Return:

1. complete source files,
2. test files,
3. workflow graph diagram,
4. state transition diagram,
5. retry strategy explanation,
6. guardrails placement explanation,
7. checkpoint/recovery explanation,
8. streaming design explanation,
9. human approval flow explanation,
10. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Workflow Module** that provides:

- LangGraph-based orchestration,
- guardrails at every generation step,
- state persistence and checkpointing,
- retry with backoff,
- streaming progress,
- human-in-the-loop approval,
- comprehensive event emission,
- and production-grade testing

for the Tailr platform.

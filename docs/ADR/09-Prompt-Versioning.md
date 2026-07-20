# ADR-0009: Adopt a Prompt Registry with Immutable Versioning and Evaluation

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr relies on prompts for every AI capability.

Examples include:

- Resume Analysis
- Job Description Analysis
- Planning
- Retrieval Query Generation
- Resume Rewriting
- Guardrail Repair
- Validation
- ATS Scoring
- Evaluation and Benchmarking

As the platform evolves, prompts will be improved continuously through experimentation and evaluation.

Embedding prompt text directly in source code creates several problems:

- difficult rollback,
- no experiment tracking,
- poor reproducibility,
- hard debugging,
- no audit history,
- inconsistent agent behavior,
- inability to compare prompt performance across releases.

Prompts should therefore be treated as **versioned production assets** rather than embedded strings.

---

# Decision

Tailr adopts a **Prompt Registry** with **immutable prompt versions** and a formal **prompt lifecycle**.

Every prompt:

- has a unique identifier,
- maintains semantic versions,
- stores metadata,
- defines a variable schema,
- records evaluation metrics,
- supports rollback,
- supports environment-specific resolution,
- can participate in A/B experiments.

Agents reference **prompt IDs** rather than prompt text.

---

# Decision Drivers

The prompt management system must:

- support version history,
- enable safe experimentation,
- provide reproducibility,
- allow instant rollback,
- separate prompts from code,
- integrate with observability,
- support A/B testing,
- support schema validation,
- enable future prompt signing.

---

# Architecture

<CodeBlock language="text" content="Agent
│
▼
Prompt Resolver
│
▼
Prompt Registry
│
▼
Prompt Version
│
▼
Template Engine
│
▼
LLM Router
│
▼
Provider Adapter
│
▼
LLM"/>

Business logic never embeds prompt text directly.

---

# Prompt Registry

Each prompt contains:

- prompt_id,
- name,
- current_production_version,
- owner,
- description,
- category,
- tags,
- created_at,
- updated_at.

Example:

<CodeBlock language="text" content="Prompt ID: resume_rewriter

Versions:

- 1.0.0
- 1.1.0
- 1.2.0
- 2.0.0"/>

---

# Immutable Prompt Versions

Each version stores:

- semantic version,
- template,
- variable schema,
- model compatibility,
- default generation parameters,
- guardrail profile,
- evaluation status,
- checksum,
- status,
- created_at.

Once created, a prompt version **cannot be modified**.

Any change requires a new version.

---

# Semantic Versioning

Tailr uses **Semantic Versioning**.

<CodeBlock language="text" content="MAJOR.MINOR.PATCH"/>

Examples:

<CodeBlock language="text" content="1.0.0
1.1.0
1.1.1
2.0.0"/>

### MAJOR

Breaking behavioral changes or output contract changes.

### MINOR

Improved reasoning or optimization quality.

### PATCH

Grammar, formatting, or instruction clarifications that do not materially change behavior.

---

# Prompt Template

Prompts use **Jinja2 templates**.

<CodeBlock language="jinja" content="You are an expert technical resume writer.

Job Description:
{{ job_description }}

Resume Context:
{{ resume_context }}

Optimization Goals:
{{ optimization_goals }}

Return only valid JSON matching the provided schema."/>

Variables are injected at runtime by the Prompt Resolver.

---

# Variable Schema

Each prompt defines a typed variable schema.

Example:

<CodeBlock language="json" content="{
"type": "object",
"required": [
"job_description",
"resume_context"
],
"properties": {
"job_description": { "type": "string" },
"resume_context": { "type": "string" },
"optimization_goals": {
"type": "array",
"items": { "type": "string" }
}
}
}"/>

Invalid variables fail before the LLM call.

---

# Prompt Metadata

Example metadata:

<CodeBlock language="json" content="{
"prompt_id": "resume_rewriter",
"version": "1.2.0",
"compatible_models": ["qwen3:14b", "llama3:70b"],
"default_temperature": 0.2,
"owner": "AI Team",
"guardrail_profile": "rewrite_strict",
"status": "production"
}"/>

Metadata supports auditing, debugging, and routing decisions.

---

# Storage Strategy

Prompts are stored in PostgreSQL.

Core tables:

<CodeBlock language="text" content="prompts
prompt_versions
prompt_experiments
prompt_evaluations
prompt_deployments
prompt_audit_logs"/>

Templates are loaded dynamically and cached in memory.

---

# Prompt Resolution

The Prompt Resolver selects the appropriate version.

Resolution order:

<CodeBlock language="text" content="Explicit version
   ↓
Experiment assignment
   ↓
Environment override
   ↓
Production version"/>

This enables safe experimentation without code changes.

---

# Environment-Aware Resolution

Different environments may use different prompt versions.

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Environment</Table.Cell><Table.Cell>Example Version</Table.Cell></Table.Row><Table.Row><Table.Cell>development</Table.Cell><Table.Cell>2.0.0-beta</Table.Cell></Table.Row><Table.Row><Table.Cell>staging</Table.Cell><Table.Cell>1.3.0-rc1</Table.Cell></Table.Row><Table.Row><Table.Cell>production</Table.Cell><Table.Cell>1.2.0</Table.Cell></Table.Row></Table>

Production remains isolated from experimental prompts.

---

# Evaluation Integration

Every prompt version records:

- success rate,
- latency,
- token usage,
- hallucination rate,
- guardrail pass rate,
- validation score,
- ATS improvement,
- user acceptance rate,
- retrieval relevance (where applicable).

Poor-performing prompts are automatically flagged for review.

---

# A/B Testing

The registry supports controlled experiments.

Example:

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Variant</Table.Cell><Table.Cell align="end">Traffic</Table.Cell></Table.Row><Table.Row><Table.Cell>1.2.0</Table.Cell><Table.Cell align="end">90%</Table.Cell></Table.Row><Table.Row><Table.Cell>1.3.0</Table.Cell><Table.Cell align="end">10%</Table.Cell></Table.Row></Table>

Assignments are deterministic per user/workflow to ensure reproducibility.

---

# Canary Rollout

New prompt versions can be deployed gradually.

<CodeBlock language="text" content="5% → 10% → 25% → 50% → 100%"/>

Rollout can be stopped instantly if metrics regress.

---

# Rollback

Example:

<CodeBlock language="text" content="Deploy 1.3.0
   ↓
Validation regressions detected
   ↓
Promote 1.2.0
   ↓
Traffic restored"/>

Rollback requires **no code deployment** and completes in seconds.

---

# Prompt Lifecycle

<CodeBlock language="text" content="Draft
↓
Review
↓
Testing
↓
Evaluation
↓
Canary
↓
Production
↓
Deprecated
↓
Archived"/>

Only **Production** prompts may be used by customer-facing workflows.

---

# Guardrails Integration

Each prompt references a **Guardrail Profile**.

Example profiles:

- `rewrite_strict`
- `analysis_standard`
- `validation_paranoid`
- `repair_mode`

The Guardrails Engine uses this profile to apply task-specific validation rules.

---

# Security

The Prompt Registry enforces:

- immutable versions,
- role-based access control,
- audit logs,
- checksum verification,
- environment isolation,
- future prompt signing.

Every prompt change is attributable to a user and timestamp.

---

# Observability

Every inference logs:

- workflow_id,
- agent_name,
- prompt_id,
- prompt_version,
- provider,
- model,
- latency,
- input tokens,
- output tokens,
- validation result,
- guardrail outcome,
- experiment assignment.

Logs are exported through **OpenTelemetry** and correlated with workflow traces.

---

# Git Integration

Prompts can be exported as files for code review.

<CodeBlock language="text" content="prompts/
└── resume_rewriter/
 ├── 1.2.0.jinja
 ├── 1.2.0.schema.json
 └── metadata.yaml"/>

Git becomes the review mechanism, while PostgreSQL remains the runtime source of truth.

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
- Requires code deployment

**Decision:** Rejected

---

## Option 2 — Prompt Files on Disk

### Advantages

- Easier maintenance
- Git version control

### Disadvantages

- Runtime updates require deployment
- Limited metadata
- No experiment tracking
- Weak observability

**Decision:** Rejected

---

## Option 3 — Prompt Registry with Immutable Versioning

### Advantages

- Full version history
- Instant rollback
- Dynamic loading
- Evaluation support
- Experiment tracking
- Better observability
- Production-ready governance

### Disadvantages

- Additional database schema
- Registry operational overhead
- Requires prompt governance process

**Decision:** Accepted

---

# Consequences

## Positive

- Reproducible AI behavior
- Safe experimentation
- Instant rollback
- Better debugging
- Prompt analytics
- Cleaner architecture
- Auditability
- Environment isolation

---

## Negative

- Additional infrastructure
- Prompt governance required
- Slight runtime lookup overhead
- More operational processes

---

# Risks

| Risk                     | Mitigation                 |
| ------------------------ | -------------------------- |
| Prompt drift             | Immutable versions         |
| Breaking prompt changes  | Semantic versioning        |
| Registry growth          | Archive deprecated prompts |
| Variable mismatches      | Schema validation          |
| Experiment contamination | Deterministic assignment   |
| Unauthorized changes     | RBAC and audit logs        |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
Workflow Engine
│
▼
AI Agent
│
▼
Prompt Resolver
│
▼
Prompt Registry
│
▼
Template Engine
│
▼
LLM Router
│
▼
Provider Adapter
│
▼
LLM"/>

The Prompt Registry is the **authoritative source for all AI prompts**.

---

# Future Enhancements

Planned enhancements include:

- prompt signing,
- automated prompt optimization,
- semantic prompt diffing,
- prompt lineage graphs,
- learned prompt selection,
- reinforcement learning from evaluations,
- prompt cost optimization,
- organization-wide prompt sharing.

The current design supports these capabilities without changing agent contracts.

---

# Related ADRs

- ADR-0005 — LlamaIndex as the AI Data and Workflow Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0008 — LLM Router and Provider Abstraction Layer

---

# References

- llm-prompt-design.md
- observability.md
- validation-engine.md
- database-design.md
- evaluation-architecture.md
- guardrails-architecture.md

---

# Review Notes

This decision should be revisited if:

- prompts are replaced by learned policies,
- fine-tuned models eliminate most prompt engineering,
- a dedicated prompt management platform becomes strategically preferable,
- or operational overhead exceeds the benefits of centralized prompt governance.

Until then, the **Prompt Registry with immutable versioning remains the authoritative source for all prompts within Tailr**, providing reproducibility, safe experimentation, rollback capability, structured governance, and full observability.

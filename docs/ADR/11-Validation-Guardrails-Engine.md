# ADR-0011: Adopt a Validation and Guardrails Engine for AI Output Safety and Integrity

**Status:** Accepted
**Date:** 2026-07-20

---

# Context

Tailr generates resume content using Large Language Models (LLMs).

AI-generated outputs are probabilistic and may contain:

- hallucinated experience,
- invented skills,
- unsupported metrics,
- malformed JSON,
- prompt injection artifacts,
- ATS-incompatible formatting,
- unsafe LaTeX commands,
- inconsistent employment dates,
- or other policy violations.

Because Tailr produces documents that may be submitted to employers, incorrect or fabricated content is unacceptable.

A deterministic validation layer is required between AI generation and downstream business logic.

---

# Decision

Tailr adopts a dedicated **Validation and Guardrails Engine (VGE)** that executes after every AI generation step.

The engine is responsible for:

- schema validation,
- JSON validation,
- hallucination detection,
- resume integrity validation,
- prompt injection detection,
- PII and secret scanning,
- ATS validation,
- LaTeX safety validation,
- automatic repair of recoverable issues,
- and structured approval/rejection decisions.

No AI-generated content may proceed to rendering or persistence without passing the Guardrails Engine.

---

# Decision Drivers

The solution must:

- prevent fabricated resume content,
- provide deterministic validation,
- support automatic repair,
- enforce ATS compatibility,
- protect the rendering pipeline,
- support auditability,
- integrate with workflow orchestration,
- and provide measurable quality metrics.

---

# Architectural Role

```text
AI Agent
   │
   ▼
Guardrails Engine
   │
   ├── Schema Validator
   ├── JSON Validator
   ├── Hallucination Detector
   ├── Resume Integrity Validator
   ├── Prompt Injection Detector
   ├── PII / Secret Scanner
   ├── ATS Validator
   ├── LaTeX Safety Validator
   └── Repair Engine
           │
           ▼
Validation Result
           │
     ┌─────┴─────┐
     ▼           ▼
Approved      Rejected
```

The Guardrails Engine acts as the trust boundary between probabilistic AI generation and deterministic business logic.

---

# Validation Pipeline

```text
Raw LLM Output
      ↓
JSON Parse
      ↓
Schema Validation
      ↓
Hallucination Check
      ↓
Integrity Validation
      ↓
Security Scan
      ↓
ATS Validation
      ↓
LaTeX Validation
      ↓
Repair (if possible)
      ↓
Approved / Rejected
```

Each stage produces a structured validation result.

---

# Validation Result Schema

```json
{
  "status": "approved",
  "repair_applied": false,
  "violations": [],
  "warnings": [],
  "metadata": {
    "validator_count": 8,
    "execution_time_ms": 42
  }
}
```

Possible statuses:

- approved
- repaired
- rejected

---

# Hallucination Detection

Generated content is compared against the **Canonical Resume Model**.

The validator detects:

- invented employers,
- invented projects,
- invented technologies,
- invented certifications,
- unsupported metrics,
- altered employment dates.

Example:

```text
Generated: "Built Kubernetes operator"
Source resume: no Kubernetes experience found
Result: REJECTED
```

This is the most critical validation stage.

---

# Resume Integrity Validation

Ensures the generated resume remains internally consistent.

Checks include:

- chronological ordering,
- non-overlapping employment dates,
- valid section references,
- skill-to-project consistency,
- project date validity,
- summary claims supported by experience.

---

# Prompt Injection Detection

Retrieved context and job descriptions are scanned for malicious instructions.

Examples:

- "Ignore previous instructions"
- "Reveal system prompt"
- "Return hidden memory"
- "Output internal configuration"

Detected injections are removed before prompt assembly.

---

# ATS Validation

Ensures the output remains ATS compatible.

Checks include:

- unsupported Unicode,
- excessive special characters,
- keyword stuffing,
- malformed contact information,
- inconsistent section headings,
- excessively long bullet points.

Warnings may be returned even when the output is approved.

---

# LaTeX Safety Validation

Because Tailr renders LaTeX deterministically, generated text must be safe to insert into templates.

Blocked commands include:

- \\input
- \\include
- \\write18
- \\openout
- \\catcode

Special characters are escaped automatically.

Unsafe LaTeX results in rejection.

---

# Repair Engine

Recoverable issues are automatically repaired.

Supported repairs:

| Issue                    | Repair             |
| ------------------------ | ------------------ |
| Unescaped %              | Escape character   |
| Invalid JSON quotes      | Normalize quotes   |
| Trailing commas          | Remove commas      |
| Extra markdown fences    | Strip fences       |
| Whitespace normalization | Trim and normalize |

If repair succeeds, the output status becomes **repaired** and the repair is logged.

---

# Guardrail Profiles

Different tasks require different validation strictness.

## rewrite_strict

- hallucination detection,
- integrity validation,
- ATS validation,
- LaTeX validation.

## analysis_standard

- schema validation,
- JSON validation,
- prompt injection detection.

## validation_paranoid

- all validators enabled,
- zero warnings tolerated,
- used before final PDF rendering.

---

# Workflow Integration

```text
Rewrite Agent
      ↓
Guardrails Engine
      ↓
Validation Agent
      ↓
ATS Agent
      ↓
Rendering Engine
```

The workflow cannot continue if guardrails reject the output.

---

# Failure Handling

## Approved

Workflow continues.

## Repaired

Workflow continues and the repair is logged.

## Rejected

Workflow transitions to **Failed** and returns a structured error.

Example:

```json
{
  "error": "hallucination_detected",
  "message": "Generated technology not present in source resume",
  "section": "projects"
}
```

---

# Audit Storage

All validation events are persisted in PostgreSQL.

Suggested schema:

```text
guardrail_events
- id
- workflow_id
- validator_name
- severity
- violation_code
- repaired
- metadata (JSONB)
- created_at
```

This enables debugging, evaluation, and compliance auditing.

---

# Observability

Every validation run records:

- workflow_id,
- agent_name,
- guardrail_profile,
- validation status,
- execution latency,
- violation count,
- repair count,
- hallucination detection outcome.

Metrics exported:

- guardrail pass rate,
- rejection rate,
- repair rate,
- hallucination rate,
- validation latency,
- prompt injection detection count.

Telemetry is exported through **OpenTelemetry** and correlated with workflow traces.

---

# Evaluation Integration

Guardrail effectiveness is continuously measured.

Tracked metrics:

- hallucination precision,
- hallucination recall,
- false positive rate,
- repair success rate,
- ATS validation accuracy,
- LaTeX validation accuracy.

These metrics are integrated into the **Evaluation Pipeline** defined in ADR-0010.

---

# Alternatives Considered

## Option 1 — Trust LLM Output

### Advantages

- simplest implementation,
- lowest latency.

### Disadvantages

- high hallucination risk,
- unsafe rendering,
- no auditability,
- unacceptable for production.

**Decision:** Rejected

---

## Option 2 — LLM-Based Self-Validation

### Advantages

- flexible,
- easy to prototype.

### Disadvantages

- probabilistic,
- can validate its own hallucinations,
- expensive,
- difficult to guarantee correctness.

**Decision:** Rejected

---

## Option 3 — Deterministic Validation and Guardrails Engine

### Advantages

- reproducible,
- testable,
- auditable,
- secure,
- integrates with CI/CD,
- prevents fabricated resume content.

### Disadvantages

- additional infrastructure,
- ongoing rule maintenance,
- stricter engineering discipline required.

**Decision:** Accepted

---

# Consequences

## Positive

- trustworthy resume generation,
- deterministic validation,
- reduced hallucinations,
- safer LaTeX rendering,
- better ATS compatibility,
- full audit trail,
- measurable quality metrics.

## Negative

- additional processing latency,
- more infrastructure components,
- rule maintenance overhead,
- occasional false positives requiring tuning.

---

# Risks

| Risk                 | Mitigation                               |
| -------------------- | ---------------------------------------- |
| False positives      | Tune validators and add review workflows |
| Rule drift           | Version validation rules                 |
| Performance overhead | Parallelize independent validators       |
| New attack patterns  | Add pluggable validator modules          |
| Excessive strictness | Use profile-based validation             |

---

# Architecture Integration

```text
FastAPI
   │
   ▼
Workflow Engine
   │
   ▼
AI Agents
   │
   ▼
Guardrails Engine
   │
   ▼
Validation Result
   │
   ▼
ATS Engine
   │
   ▼
Rendering Engine
   │
   ▼
PDF Artifact
```

The Guardrails Engine is a mandatory quality gate before persistence and rendering.

---

# Future Enhancements

Planned enhancements include:

- semantic contradiction detection,
- organization-specific policy packs,
- learned anomaly detection,
- multi-model consensus validation,
- cryptographic prompt signing,
- compliance rule engine,
- streaming guardrails,
- and differential resume comparison.

The architecture is designed to support these capabilities without changing agent contracts.

---

# Related ADRs

- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture with Hexagonal Boundaries
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0008 — LLM Router and Provider Abstraction Layer
- ADR-0009 — Prompt Registry with Immutable Versioning
- ADR-0010 — Evaluation-Driven Development

---

# References

- 20-Guardrails-Architecture.md
- validation-engine.md
- evaluation-architecture.md
- workflow-design.md
- observability.md

---

# Review Notes

This decision should be revisited if:

- deterministic validation is replaced by formally verified generation techniques,
- rendering no longer depends on LaTeX,
- or organizational policy requirements change significantly.

Until then, the **Validation and Guardrails Engine remains the mandatory trust boundary for all AI-generated content in Tailr**, ensuring factual integrity, ATS compatibility, rendering safety, and full auditability before any resume content is persisted or rendered into a final PDF artifact.

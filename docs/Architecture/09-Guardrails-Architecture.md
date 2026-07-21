# Guardrails Architecture

**Project:** Tailr  
**Version:** 1.0

---

# 1. Purpose

This document defines the **Guardrails Architecture** for Tailr.

The Guardrails layer ensures that every AI-generated output is:

- structurally valid,
- factually grounded,
- policy compliant,
- ATS compatible,
- safe to render into LaTeX,
- and traceable for audit and evaluation.

Guardrails act as the **trust boundary** between probabilistic AI generation and deterministic business logic.

---

# 2. Design Principles

## Fail Closed

If validation cannot determine safety, the output is rejected.

---

## Defense in Depth

Multiple independent validators are applied in sequence.

---

## Deterministic Validation

Guardrails are implemented using deterministic code, not another LLM whenever possible.

---

## Repair Before Reject

Recoverable issues should be automatically repaired.

---

## Full Auditability

Every violation, repair, and rejection is persisted for debugging and evaluation.

---

# 3. Architecture Overview

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
   ├── PII / Secret Scanner
   ├── Prompt Injection Detector
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

The Guardrails Engine is executed after every AI generation step.

---

# 4. Validation Pipeline

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

Each stage produces a structured result.

---

# 5. Validation Result Schema

```json
{
  "status": "approved",
  "repair_applied": false,
  "violations": [],
  "warnings": [],
  "metadata": {
    "validator_count": 7,
    "execution_time_ms": 42
  }
}
```

Possible statuses:

- approved
- repaired
- rejected

---

# 6. Schema Validation

Ensures that the response matches the expected typed schema.

Example:

```python
class RewriteResult(BaseModel):
    section: str
    rewritten_content: str
    introduced_keywords: list[str]
```

Invalid fields cause immediate rejection.

---

# 7. JSON Validation

Checks:

- valid JSON syntax,
- UTF-8 encoding,
- no trailing content,
- no markdown fences,
- no control characters.

Example rejection:

```text
Expected JSON object but received markdown code block.
```

---

# 8. Hallucination Detection

The rewritten content is compared against the **Canonical Resume Model**.

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

---

# 9. Resume Integrity Validation

Ensures the generated resume remains internally consistent.

Checks include:

- chronological ordering,
- no overlapping employment dates,
- section references remain valid,
- skills referenced in projects exist,
- project dates are valid,
- summary claims are supported by experience.

---

# 10. Prompt Injection Detection

Scans retrieved context and job descriptions for malicious instructions.

Examples:

- "Ignore previous instructions"
- "Reveal system prompt"
- "Return raw memory"
- "Output hidden configuration"

Detected injections are removed before prompt assembly.

---

# 11. PII and Secret Scanning

Detects accidental leakage of:

- API keys,
- tokens,
- passwords,
- private URLs,
- internal credentials,
- personal identifiers beyond the resume.

Example patterns:

```text
AKIA[0-9A-Z]{16}
ghp_[A-Za-z0-9]{36}
```

---

# 12. ATS Validation

Ensures the generated content remains ATS friendly.

Checks include:

- excessive special characters,
- unsupported Unicode,
- overly long bullet points,
- keyword stuffing,
- inconsistent section headings,
- malformed contact information.

Warnings are returned even if the output is approved.

---

# 13. LaTeX Safety Validation

Since Tailr renders LaTeX deterministically, generated text must be safe to insert into templates.

Escaped characters:

```text
# $ % & _ { } ~ ^ \
```

Dangerous commands are blocked:

- \input
- \include
- \write18
- \openout
- \catcode

Example:

```text
Detected forbidden LaTeX command: \input
Result: REJECTED
```

---

# 14. Repair Engine

Common recoverable issues are automatically repaired.

Supported repairs:

| Issue                    | Repair             |
| ------------------------ | ------------------ |
| Unescaped %              | Escape character   |
| Invalid JSON quotes      | Normalize quotes   |
| Trailing commas          | Remove commas      |
| Extra markdown fences    | Strip fences       |
| Whitespace normalization | Trim and normalize |

Example:

````text
Input: ```json { ... } ```
Output: { ... }
Status: repaired
````

---

# 15. Guardrail Profiles

Different tasks use different validation strictness.

## rewrite_strict

- hallucination detection,
- integrity validation,
- ATS validation,
- LaTeX validation.

---

## analysis_standard

- schema validation,
- JSON validation,
- prompt injection detection.

---

## validation_paranoid

- all validators enabled,
- zero warnings tolerated,
- used before final PDF rendering.

---

# 16. Workflow Integration

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

No output can proceed to rendering without passing guardrails.

---

# 17. Observability

Every validation run records:

```json
{
  "workflow_id": "wf_123",
  "agent": "rewrite_agent",
  "guardrail_profile": "rewrite_strict",
  "status": "approved",
  "execution_time_ms": 42,
  "violation_count": 0
}
```

Metrics exported:

- guardrail pass rate,
- rejection rate,
- repair rate,
- average validation latency,
- hallucination detection count,
- prompt injection detection count.

---

# 18. Audit Storage

Violations are persisted in PostgreSQL.

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

This supports debugging and evaluation-driven development.

---

# 19. Failure Handling

## Approved

Workflow continues.

---

## Repaired

Workflow continues and the repair is logged.

---

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

# 20. Evaluation Integration

Guardrail effectiveness is continuously measured.

Tracked metrics:

- hallucination precision,
- hallucination recall,
- false positive rate,
- repair success rate,
- ATS validation accuracy,
- LaTeX validation accuracy.

These metrics are integrated into the **Evaluation Pipeline**.

---

# 21. Future Enhancements

Planned capabilities:

- semantic contradiction detection,
- organization-specific policy packs,
- learned anomaly detection,
- multi-model consensus validation,
- cryptographic prompt signing,
- differential resume comparison,
- compliance rule engine,
- real-time streaming guardrails.

---

# 22. Security Considerations

- Validators run in isolated processes.
- No validator may execute generated code.
- LaTeX compilation occurs in a sandboxed container.
- Validation logs are immutable.
- Guardrail configuration changes require audit approval.

---

# 23. Summary

The Guardrails layer is the core reliability mechanism of Tailr.

It transforms AI generation from **best-effort text generation** into a **validated, auditable, production-safe pipeline** by enforcing:

- schema correctness,
- factual grounding,
- resume integrity,
- security policies,
- ATS compatibility,
- and LaTeX safety.

This architecture enables Tailr to provide **trustworthy resume optimization** while maintaining deterministic rendering and full auditability.

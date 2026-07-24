# Business Validation Engine

**Project:** Tailr
**Version:** 1.0

# 1. Purpose

The Business Validation Engine is responsible for verifying every AI-generated artifact after it has been approved or repaired by the Guardrails Engine.

Its primary objectives are to enforce business rules, verify formatting, validate keyword coverage, ensure ATS compliance, and guarantee that generated resumes meet quality standards.

The Business Validation Engine operates only on content that has already passed the Guardrails Engine (see [09-Guardrails-Architecture.md](09-Guardrails-Architecture.md) for AI safety validation including hallucination detection, prompt injection detection, schema validation, PII scanning, and LaTeX safety).

The Validation Engine is deterministic and does not rely on LLM reasoning for its core validation logic.

# 2. Design Goals

The Validation Engine must:

- Prevent hallucinated content
- Preserve immutable facts
- Validate schemas
- Enforce business rules
- Detect formatting issues
- Produce explainable validation reports
- Support automatic retries
- Detect prompt injection
- Detect PII leakage
- Support output repair
- Provide auditability and traceability

# 3. Validation Philosophy

Tailr follows four validation principles.

## Trust Nothing

Every AI response is treated as untrusted input.

## Validate Before Persisting

Artifacts are validated before:

- Rendering
- PDF generation
- Database storage
- User approval

## Layered Validation

Validation occurs in multiple stages.

Each layer has a single responsibility.

## Explainable Failures

Every failed validation produces structured, actionable feedback.

# 4. Validation Pipeline

```
                AI Output
                    │
                    ▼
           Guardrails Engine
      (See 09-Guardrails-Architecture)
                    │
                    ▼
       Guardrails-Approved Output
                    │
                    ▼
       Canonical Model Validation
                    │
                    ▼
       Business Rule Validation
                    │
                    ▼
          Keyword Validation
                    │
                    ▼
        Formatting Validation
                    │
                    ▼
          Validation Report
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
        PASS               FAIL
          │                   │
          ▼                   ▼
      Continue        Retry / Repair / Reject
```

# 5. Validation Levels

Tailr performs six validation layers.

| Layer      | Purpose                         |
| ---------- | ------------------------------- |
| Schema     | Structural correctness          |
| Domain     | Valid domain entities           |
| Business   | Resume rules                    |
| Knowledge  | Compare against canonical facts |
| ATS        | ATS compatibility               |
| Formatting | Rendering safety                |

> **Note:** AI safety validation (prompt injection, hallucination detection, PII scanning, LaTeX safety) is handled by the Guardrails Engine, which runs **before** this Validation Engine. See [09-Guardrails-Architecture.md](09-Guardrails-Architecture.md).

# 6. Schema Validation

> **Note:** JSON parsing, prompt injection detection, PII scanning, hallucination detection, and LaTeX safety validation are handled by the Guardrails Engine before this Validation Engine receives the output. This section describes the business-level schema checks that run after Guardrails approval.

Every Guardrails-approved response is further validated against business schemas.

Example

```json
{
  "summary": "...",
  "projects": [],
  "experience": []
}
```

Validation checks:

- Required fields
- Data types
- Missing values
- Unknown fields
- Enum constraints

Failure immediately rejects the output.

# 8. Canonical Model Validation

The generated resume is compared against the canonical knowledge model.

Immutable facts include:

- Company names
- Job titles
- Employment dates
- Education
- Project names
- Technologies actually used

Example

```
Canonical

Python

↓

Generated

Java

↓

FAIL
```

# 9. Business Rule Validation

Business rules enforce resume quality.

Examples

- Every experience entry must contain at least one bullet.
- Dates must be chronological.
- Duplicate skills are not allowed.
- Empty sections are prohibited.
- Bullet counts must remain within configured limits.

Business rules are deterministic.

# 10. Hallucination Detection

The engine detects unsupported claims.

Checks include:

- Unknown technologies
- Fabricated employers
- Invented metrics
- New certifications
- Additional projects
- Modified achievements

Every generated fact must be traceable to canonical knowledge.

# 11. Semantic Consistency

Validation compares meaning rather than exact wording.

Example

Original

```
Developed REST APIs using FastAPI.
```

Generated

```
Built scalable REST APIs with FastAPI.
```

PASS

Example

Original

```
FastAPI
```

Generated

```
Spring Boot
```

FAIL

Semantic similarity is measured using embeddings and canonical mappings.

# 12. Keyword Validation

Checks:

- Required JD keywords covered
- Duplicate keyword stuffing
- Missing critical technologies
- ATS keyword balance

The goal is optimization, not excessive repetition.

# 13. Formatting Validation

Before rendering:

- Valid LaTeX escaping
- No broken commands
- Line length limits
- UTF-8 compliance
- Template compatibility

This prevents compilation failures.

# 14. Security Validation

Reject:

- Prompt injection artifacts
- HTML/JavaScript
- Embedded instructions
- Hidden control characters
- Suspicious Unicode
- System prompt extraction attempts
- Encoded payloads
- External command references

User-provided content is always sanitized.

# 15. Validation Report

Every execution generates a structured report.

```json
{
  "status": "approved",
  "repair_applied": false,
  "errors": [],
  "warnings": ["Missing AWS keyword"],
  "ats_score": 87,
  "confidence": 0.98,
  "trace_id": "wf_123456"
}
```

Reports are stored for debugging and analytics.

# 16. Error Classification

Validation issues are categorized.

```
INFO

WARNING

ERROR

CRITICAL
```

Only ERROR and CRITICAL block workflow progression.

# 17. Retry & Repair Strategy

On failure:

```
Validation Failed
        │
        ▼
Identify Failing Rules
        │
        ▼
Attempt Automatic Repair
        │
        ▼
Revalidate
        │
        ▼
Repair Prompt
        │
        ▼
Rewrite
        │
        ▼
Revalidate
```

Automatic repairs may include:

- Fix malformed JSON
- Remove unknown fields
- Normalize technology names
- Escape invalid LaTeX characters
- Remove duplicate keywords

Maximum retry count is configurable.

If retries fail, the workflow requests manual review.

# 18. Human Review

Some issues require user confirmation.

Examples:

- Ambiguous wording
- Low confidence rewrites
- Multiple valid alternatives

The user always has final approval.

# 19. Validation Metrics

The engine records:

- Pass rate
- Retry rate
- Hallucination rate
- Schema failures
- Average validation latency
- Business rule violations
- Repair rate
- Prompt injection rate
- PII violation rate
- ATS failures
- Guardrail violation counts by severity

Metrics feed observability dashboards.

# 20. Integration Points

The Validation Engine integrates with:

- Parser
- Workflow Engine
- AI Agents
- Renderer
- Knowledge Layer
- ATS Advisor
- Prompt Builder
- Telemetry System
- Audit Logging System

Every generated artifact passes through validation before downstream processing.

# 21. Testing Strategy

Validation rules are tested using:

- Unit tests
- Golden datasets
- Regression tests
- Adversarial prompts
- Fuzz testing
- Property-based testing
- Prompt injection tests
- PII leakage tests
- Malformed JSON tests
- Output repair tests

Validation logic must be deterministic.

# 22. Future Enhancements

Planned capabilities:

- LLM-as-a-judge (secondary opinion)
- Cross-model consensus validation
- Knowledge graph verification
- Recruiter preference validation
- Industry-specific rule packs
- Continuous rule learning from user feedback

Deterministic validation remains the primary authority.

# 23. Architecture Decisions

| Decision                        | Rationale                         |
| ------------------------------- | --------------------------------- |
| Deterministic validation        | Avoid LLM uncertainty             |
| Centralized Guardrails Pipeline | Consistent AI safety enforcement  |
| Canonical knowledge comparison  | Prevent hallucinations            |
| Layered validation              | Easier maintenance                |
| Structured reports              | Explainability                    |
| Automatic repair                | Improve reliability               |
| Automatic retries               | Recover transient failures        |
| Human approval                  | Preserve user control             |
| Versioned validation rules      | Reproducibility                   |
| Provider-independent guardrails | Consistent behavior across models |
| Audit logging                   | Compliance and debugging          |

# 24. Summary

The Validation & Guardrails Engine is the quality and safety gate for Tailr.

Rather than trusting AI output, every generated artifact passes through a deterministic validation pipeline that enforces:

- AI safety
- Prompt injection protection
- Schema correctness
- Business rules
- Factual consistency
- Resume integrity
- ATS compatibility
- Formatting safety
- Security constraints

This layered approach ensures that only validated, explainable, auditable, and reliable content progresses through the workflow.

By separating guardrails from business validation and grounding every generated claim in canonical knowledge, Tailr can deliver production-quality resume optimizations with minimal hallucination risk, strong protection against prompt injection and data leakage, and a fully traceable validation history suitable for enterprise-grade AI systems.

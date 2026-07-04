# Validation Engine

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

The Validation Engine is responsible for verifying every AI-generated artifact before it becomes part of the workflow.

Its primary objective is to prevent hallucinations, preserve factual accuracy, enforce business rules, and guarantee that generated resumes remain consistent with the canonical knowledge model.

The Validation Engine is deterministic and does not rely on LLM reasoning for its core validation logic.

---

# 2. Design Goals

The Validation Engine must:

- Prevent hallucinated content
- Preserve immutable facts
- Validate schemas
- Enforce business rules
- Detect formatting issues
- Produce explainable validation reports
- Support automatic retries

---

# 3. Validation Philosophy

Tailr follows four validation principles.

## Trust Nothing

Every AI response is treated as untrusted input.

---

## Validate Before Persisting

Artifacts are validated before:

- Rendering
- PDF generation
- Database storage
- User approval

---

## Layered Validation

Validation occurs in multiple stages.

Each layer has a single responsibility.

---

## Explainable Failures

Every failed validation produces structured, actionable feedback.

---

# 4. Validation Pipeline

```
                AI Output
                    │
                    ▼
           JSON Schema Validation
                    │
                    ▼
          Canonical Model Validation
                    │
                    ▼
          Business Rule Validation
                    │
                    ▼
        Hallucination Detection
                    │
                    ▼
        Formatting Validation
                    │
                    ▼
          Validation Report
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       PASS                FAIL
          │                   │
          ▼                   ▼
      Continue             Retry / Reject
```

---

# 5. Validation Levels

Tailr performs six validation layers.

| Layer      | Purpose                         |
| ---------- | ------------------------------- |
| Schema     | Structural correctness          |
| Domain     | Valid domain entities           |
| Business   | Resume rules                    |
| Knowledge  | Compare against canonical facts |
| Formatting | Rendering safety                |
| Security   | Detect malicious content        |

---

# 6. Schema Validation

Every AI response must match predefined Pydantic schemas.

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

---

# 7. Canonical Model Validation

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

---

# 8. Business Rule Validation

Business rules enforce resume quality.

Examples

- Every experience entry must contain at least one bullet.
- Dates must be chronological.
- Duplicate skills are not allowed.
- Empty sections are prohibited.
- Bullet counts must remain within configured limits.

Business rules are deterministic.

---

# 9. Hallucination Detection

The engine detects unsupported claims.

Checks include:

- Unknown technologies
- Fabricated employers
- Invented metrics
- New certifications
- Additional projects
- Modified achievements

Every generated fact must be traceable to canonical knowledge.

---

# 10. Semantic Consistency

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

---

# 11. Keyword Validation

Checks:

- Required JD keywords covered
- Duplicate keyword stuffing
- Missing critical technologies
- ATS keyword balance

The goal is optimization, not excessive repetition.

---

# 12. Formatting Validation

Before rendering:

- Valid LaTeX escaping
- No broken commands
- Line length limits
- UTF-8 compliance
- Template compatibility

This prevents compilation failures.

---

# 13. Security Validation

Reject:

- Prompt injection artifacts
- HTML/JavaScript
- Embedded instructions
- Hidden control characters
- Suspicious Unicode

User-provided content is always sanitized.

---

# 14. Validation Report

Every execution generates a structured report.

```json
{
  "passed": true,
  "errors": [],
  "warnings": ["Missing AWS keyword"],
  "hallucination_score": 0.01,
  "confidence": 0.98
}
```

Reports are stored for debugging and analytics.

---

# 15. Error Classification

Validation issues are categorized.

```
INFO

WARNING

ERROR

CRITICAL
```

Only ERROR and CRITICAL block workflow progression.

---

# 16. Retry Strategy

On failure:

```
Validation Failed

↓

Identify Failing Rules

↓

Repair Prompt

↓

Rewrite

↓

Revalidate
```

Maximum retry count is configurable.

If retries fail, the workflow requests manual review.

---

# 17. Human Review

Some issues require user confirmation.

Examples:

- Ambiguous wording
- Low confidence rewrites
- Multiple valid alternatives

The user always has final approval.

---

# 18. Validation Metrics

The engine records:

- Pass rate
- Retry rate
- Hallucination rate
- Schema failures
- Average validation latency
- Business rule violations

Metrics feed observability dashboards.

---

# 19. Integration Points

The Validation Engine integrates with:

- Parser
- Workflow Engine
- AI Agents
- Renderer
- Knowledge Layer
- ATS Advisor

Every generated artifact passes through validation before downstream processing.

---

# 20. Testing Strategy

Validation rules are tested using:

- Unit tests
- Golden datasets
- Regression tests
- Adversarial prompts
- Fuzz testing
- Property-based testing

Validation logic must be deterministic.

---

# 21. Future Enhancements

Planned capabilities:

- LLM-as-a-judge (secondary opinion)
- Cross-model consensus validation
- Knowledge graph verification
- Recruiter preference validation
- Industry-specific rule packs
- Continuous rule learning from user feedback

Deterministic validation remains the primary authority.

---

# 22. Architecture Decisions

| Decision                       | Rationale              |
| ------------------------------ | ---------------------- |
| Deterministic validation       | Avoid LLM uncertainty  |
| Canonical knowledge comparison | Prevent hallucinations |
| Layered validation             | Easier maintenance     |
| Structured reports             | Explainability         |
| Automatic retries              | Improve reliability    |
| Human approval                 | Preserve user control  |

---

# 23. Summary

The Validation Engine is the quality gate for Tailr.

Rather than trusting AI output, every generated artifact passes through a deterministic validation pipeline that enforces schema correctness, business rules, factual consistency, formatting safety, and security constraints.

This layered approach ensures that only validated, explainable, and reliable content progresses through the workflow, enabling Tailr to deliver production-quality resume optimizations with minimal hallucination risk.

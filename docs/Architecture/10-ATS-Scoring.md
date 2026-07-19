# ATS Scoring Engine

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

The ATS Scoring Engine evaluates how effectively a resume aligns with a target job description.

Rather than relying solely on keyword matching, Tailr performs a comprehensive multi-factor evaluation that combines deterministic analysis with AI-assisted semantic reasoning.

The resulting score helps users understand both technical ATS compatibility and overall resume quality.

---

# 2. Design Goals

The ATS Scoring Engine must:

- Measure resume-job alignment
- Identify missing skills
- Detect keyword stuffing
- Evaluate semantic relevance
- Generate actionable recommendations
- Produce deterministic scoring
- Validate ATS compatibility before scoring
- Support configurable scoring profiles
- Provide auditability and historical comparison
- Explain every score

---

# 3. Design Philosophy

Tailr follows four scoring principles.

## Explainable

Every point gained or lost must have a reason.

---

## Deterministic

The same inputs produce the same score.

---

## Multi-Dimensional

Scores represent several independent quality dimensions.

---

## Recommendation Driven

The objective is improvement, not just scoring.

---

# 4. High-Level Architecture

```
              Resume
                  │
                  ▼
         Canonical Resume Model
                  │
                  ▼
           ATS Scoring Engine
                  │
      ┌───────────┼────────────┐
      ▼           ▼            ▼
 Keyword     Semantic      Formatting
 Analysis     Analysis       Analysis
      │           │            │
      └───────────┼────────────┘
                  ▼
          Weighted Score
                  ▼
      Recommendations Report
```

---

# 5. ATS Guardrails

Before scoring, the resume is validated for ATS compatibility.

Checks include:

- Standard section headings
- Chronological ordering
- Bullet formatting consistency
- Maximum bullet length
- No tables or multi-column layouts
- Safe LaTeX rendering
- UTF-8 compliance
- No hidden or invisible text
- No keyword stuffing patterns

If critical ATS violations are found, scoring is blocked until the resume is repaired.

# 6. Scoring Dimensions

The overall ATS score is composed of several independent dimensions.

| Dimension            | Weight |
| -------------------- | ------ |
| Keyword Coverage     | 30%    |
| Semantic Match       | 20%    |
| Experience Alignment | 15%    |
| Skills Match         | 10%    |
| Project Relevance    | 10%    |
| Resume Structure     | 5%     |
| Formatting           | 5%     |
| Readability          | 5%     |

Total = 100%

Weights are configurable.

---

# 7. Keyword Analysis

Checks:

- Required keywords
- Preferred keywords
- Missing keywords
- Frequency
- Placement
- Keyword stuffing
- Synonym coverage
- Section distribution

Keyword stuffing is penalized when the same keyword appears excessively without contextual relevance.

Example

```
Required

FastAPI

Present

PASS
```

---

# 8. Semantic Analysis

Embedding-based comparison identifies concept matches.

Example

Job Description

```
REST API Development
```

Resume

```
Built scalable backend services using FastAPI.
```

Keyword match

Low

Semantic match

High

Semantic similarity contributes to the final score.

---

# 9. Skills Match

The engine compares:

Resume Skills

↓

Job Requirements

Outputs:

- matched skills
- missing skills
- additional strengths

Skills are grouped by category.

Example

Backend

Frontend

Cloud

AI

Databases

DevOps

---

# 10. Experience Alignment

Checks include:

- Years of experience
- Domain relevance
- Role similarity
- Seniority alignment
- Industry alignment

Example

JD

Backend Engineer

Resume

Backend + AI Engineer

High alignment

---

# 11. Project Relevance

Projects are ranked by relevance.

Evaluation considers:

- technologies
- domain
- complexity
- impact
- metrics

Projects with stronger alignment receive higher scores.

---

# 12. Resume Structure

Evaluates:

- Summary
- Skills
- Experience
- Projects
- Education
- Certifications

Missing critical sections reduce the score.

---

# 13. Formatting Analysis

Checks:

- ATS-friendly LaTeX
- Consistent formatting
- Bullet structure
- Section hierarchy
- Safe PDF generation

Tailr evaluates structure rather than visual design.

---

# 14. Readability Analysis

Metrics include:

- Bullet length
- Passive voice
- Action verbs
- Sentence complexity
- Repetition

The goal is concise and impactful writing.

---

# 15. Keyword Coverage

Example report

```
Matched

FastAPI

Python

REST API

Docker

Git

Missing

Redis

AWS

Kubernetes
```

Coverage percentage is calculated automatically.

---

# 16. Recommendation Engine

Recommendations are prioritized.

Example

High Priority

- Add Redis experience if applicable
- Highlight backend API development
- Move AI project higher

Medium Priority

- Improve summary
- Increase measurable achievements

Low Priority

- Reorder skills

---

# 17. Score Calculation

```
Keyword Score

×

Weight

+

Semantic Score

×

Weight

+

Formatting Score

×

Weight

↓

Overall Score
```

Scores range from:

0–100

---

# 18. Confidence Score

The engine produces a confidence score indicating scoring reliability.

Factors include:

- JD clarity
- Resume completeness
- Keyword extraction confidence
- Semantic match confidence
- Parsing quality
- Validation results

Example

```text
ATS Score: 88
Confidence: 0.96
```

Low-confidence scores trigger a warning in the UI.

# 19. Report Model

```json
{
  "overall_score": 88,
  "confidence": 0.96,
  "keyword_score": 92,
  "semantic_score": 85,
  "skills_score": 90,
  "experience_score": 84,
  "recommendations": [],
  "missing_keywords": [],
  "keyword_density": {
    "python": 0.018,
    "fastapi": 0.012
  }
}
```

The report is stored alongside each optimization.

---

# 20. Visualization

The frontend may display:

- Overall score
- Category breakdown
- Keyword coverage
- Missing skills
- Recommendations
- Before vs After comparison

Visualizations are generated from structured data.

---

# 21. Workflow Integration

The ATS Engine runs:

```
Rewrite Completed
        ↓
Validation & Guardrails Passed
        ↓
ATS Analysis
        ↓
Recommendations Generated
        ↓
User Review
```

Only validated resumes are scored.

---

# 22. Evaluation Metrics

The scoring engine tracks:

- Average ATS score
- Improvement after optimization
- Keyword coverage
- Recommendation acceptance rate
- User satisfaction
- Confidence distribution
- False positive rate
- False negative rate
- Average scoring latency

Metrics support future model tuning.

---

# 23. Limitations

The ATS score is an approximation.

Actual applicant tracking systems differ between employers.

Tailr aims to optimize for broadly accepted ATS best practices rather than mimic any specific vendor.

---

# 24. Future Enhancements

Planned capabilities include:

- Company-specific scoring profiles
- Industry-specific scoring rules
- Recruiter preference profiles
- Resume benchmarking
- Multi-JD comparison
- Historical score trends
- Cover letter scoring
- LinkedIn profile scoring

---

# 25. Architecture Decisions

| Decision                    | Rationale                    |
| --------------------------- | ---------------------------- |
| Weighted dimensions         | Balanced evaluation          |
| Semantic matching           | Beyond keyword counting      |
| Explainable recommendations | Improve user trust           |
| Structured reports          | Easy frontend integration    |
| Configurable weights        | Future customization         |
| Deterministic scoring       | Consistent results           |
| Guardrails before scoring   | Prevent invalid ATS analysis |
| Confidence scoring          | Indicate reliability         |
| Score normalization         | Prevent inflated scores      |

---

# 26. Summary

The ATS Scoring Engine provides a comprehensive evaluation of resume quality by combining deterministic analysis with semantic relevance scoring and ATS guardrails.

Instead of producing a single opaque score, Tailr measures multiple quality dimensions, validates ATS compatibility, explains every result, and generates prioritized recommendations with estimated impact.

This approach transforms ATS analysis from a simple keyword checker into an intelligent, auditable, and production-ready resume assessment system that guides users toward measurable improvements while maintaining factual integrity and ATS compliance.

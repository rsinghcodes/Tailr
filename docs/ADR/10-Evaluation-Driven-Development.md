# ADR-0010: Adopt Evaluation-Driven Development (EDD) for AI Quality Assurance

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr's primary functionality depends on Large Language Models (LLMs).

Unlike traditional software, AI behavior is probabilistic.

A prompt change, model upgrade, embedding replacement, or retrieval strategy modification can silently degrade output quality without causing application failures.

Examples include:

- Lower ATS scores
- Missing keywords
- Hallucinated experience
- Incorrect project summaries
- Poor retrieval quality
- Invalid JSON output

Traditional unit tests cannot adequately detect these regressions.

A systematic evaluation framework is required.

---

# Decision

Tailr adopts **Evaluation-Driven Development (EDD)**.

Every AI component must be evaluated against benchmark datasets before deployment.

Evaluation becomes a mandatory stage of the development lifecycle.

No AI changes are promoted to production without passing evaluation thresholds.

---

# Decision Drivers

The evaluation framework must:

- Measure AI quality objectively
- Detect regressions automatically
- Compare prompt versions
- Compare model versions
- Evaluate retrieval quality
- Support CI/CD automation
- Enable reproducible experiments

---

# Evaluation Architecture

```
Developer Change
        │
        ▼
Evaluation Runner
        │
        ▼
Golden Dataset
        │
        ▼
AI Pipeline
        │
        ▼
Metric Calculation
        │
        ▼
Evaluation Report
        │
        ▼
Deployment Decision
```

Evaluation occurs before deployment.

---

# Evaluation Targets

Every major AI component is evaluated.

Examples include:

- Resume Analyzer
- JD Analyzer
- Planner
- Retriever
- Rewriter
- Validator
- ATS Scorer

Each component has independent benchmarks.

---

# Golden Dataset

Tailr maintains a curated dataset containing:

- Sample resumes
- Job descriptions
- Expected keywords
- Expected ATS improvements
- Expected structured outputs
- Validation outcomes

The dataset is version-controlled and immutable.

---

# Evaluation Types

## Prompt Evaluation

Measures:

- Output quality
- Schema compliance
- Token usage
- Latency

---

## Model Evaluation

Compares:

- Different LLMs
- Local vs cloud models
- Cost
- Accuracy

---

## Retrieval Evaluation

Measures:

- Precision@K
- Recall@K
- Context relevance
- Retrieval latency

---

## Workflow Evaluation

Measures:

- Workflow success rate
- End-to-end latency
- Retry frequency
- Failure rate

---

## Validation Evaluation

Measures:

- JSON validity
- Hallucination detection
- Rule compliance
- Formatting accuracy

---

# Metrics

Example metrics include:

| Metric             | Description                          |
| ------------------ | ------------------------------------ |
| Precision@K        | Retrieval accuracy                   |
| Recall@K           | Relevant information retrieved       |
| Faithfulness       | Output grounded in retrieved context |
| Hallucination Rate | Unsupported generated content        |
| ATS Improvement    | Increase in ATS score                |
| JSON Validity      | Schema compliance                    |
| Token Usage        | Cost efficiency                      |
| Latency            | Response time                        |

---

# Evaluation Workflow

```
Prompt Updated

↓

Execute Benchmarks

↓

Collect Metrics

↓

Compare Baseline

↓

Generate Report

↓

Approve or Reject
```

No deployment occurs without evaluation.

---

# Regression Detection

Example:

```
Prompt v1.2

ATS Score = 91

↓

Prompt v1.3

ATS Score = 84

↓

Regression Detected

↓

Deployment Blocked
```

The framework prevents silent quality degradation.

---

# Evaluation Reports

Every evaluation stores:

- evaluation_id
- workflow_id
- prompt_version
- model_version
- benchmark_version
- metrics
- timestamp

Results are persisted for historical comparison.

---

# Continuous Evaluation

Evaluations run:

- During development
- In CI pipelines
- Before releases
- After model upgrades
- After prompt changes
- After retrieval changes

Evaluation is continuous, not occasional.

---

# Integration with CI/CD

```
Git Push

↓

Build

↓

Unit Tests

↓

Integration Tests

↓

AI Evaluation

↓

Quality Gate

↓

Deploy
```

Deployment proceeds only if evaluation passes.

---

# Observability

Evaluation results integrate with:

- Langfuse
- OpenTelemetry
- Grafana
- Custom dashboards

Historical trends are available for analysis.

---

# Alternatives Considered

## Option 1 — Manual Testing

### Advantages

- Simple
- Low setup effort

### Disadvantages

- Subjective
- Not reproducible
- Time-consuming
- Poor regression detection

Decision: Rejected

---

## Option 2 — Unit Tests Only

### Advantages

- Fast execution
- Good for deterministic logic

### Disadvantages

- Cannot measure AI quality
- Does not detect prompt regressions

Decision: Rejected

---

## Option 3 — Evaluation-Driven Development

### Advantages

- Objective quality measurement
- Automated regression detection
- Continuous benchmarking
- Safer deployments
- Reproducible experiments

### Disadvantages

- Requires benchmark datasets
- Additional infrastructure
- Ongoing maintenance

Decision: Accepted

---

# Consequences

## Positive

- Higher AI reliability
- Reduced hallucinations
- Measurable improvements
- Safer prompt evolution
- Better model selection
- Continuous quality assurance

---

## Negative

- Benchmark maintenance
- Longer CI execution
- Increased storage for evaluation results

---

# Risks

| Risk               | Mitigation                         |
| ------------------ | ---------------------------------- |
| Benchmark bias     | Diverse evaluation datasets        |
| Dataset staleness  | Regular benchmark updates          |
| Metric overfitting | Use multiple complementary metrics |
| Evaluation cost    | Sampled and scheduled evaluations  |

---

# Architecture Integration

```
FastAPI

↓

Workflow Engine

↓

AI Agents

↓

Prompt Registry

↓

Model Provider

↓

Evaluation Framework

↓

Deployment
```

The Evaluation Framework acts as a quality gate before production.

---

# Related ADRs

- ADR-0005 — Use LlamaIndex as the AI Data Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0008 — Model Provider Abstraction Layer
- ADR-0009 — Prompt Versioning and Prompt Registry

---

# References

- Testing.md
- Validation-Engine.md
- Observability.md
- Workflow-Design.md

---

# Review Notes

This decision should be revisited if:

- deterministic AI techniques replace probabilistic generation,
- evaluation standards evolve significantly,
- or external AI evaluation platforms become the primary quality gate.

Until then, Evaluation-Driven Development remains the standard methodology for ensuring AI quality and preventing regressions within Tailr.

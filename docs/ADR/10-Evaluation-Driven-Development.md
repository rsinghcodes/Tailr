# ADR-0010: Adopt Evaluation-Driven Development (EDD) for AI Quality Assurance

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr’s primary functionality depends on Large Language Models (LLMs), retrieval pipelines, prompt templates, and guardrail policies.

Unlike traditional software, AI behavior is **probabilistic**.

A prompt change, model upgrade, embedding replacement, reranker change, or retrieval strategy modification can silently degrade output quality without causing application failures.

Examples include:

- lower ATS scores,
- missing keywords,
- hallucinated experience,
- incorrect project summaries,
- poor retrieval quality,
- invalid JSON output,
- guardrail bypasses,
- increased token usage,
- unacceptable latency.

Traditional unit tests cannot adequately detect these regressions.

A systematic evaluation framework is required to make AI quality measurable, reproducible, and enforceable.

---

# Decision

Tailr adopts **Evaluation-Driven Development (EDD)** as a mandatory engineering practice.

Every AI component must be evaluated against benchmark datasets before deployment.

Evaluation becomes a required stage of the development lifecycle and CI/CD pipeline.

No AI-related change is promoted to production unless it passes defined quality thresholds.

---

# Decision Drivers

The evaluation framework must:

- measure AI quality objectively,
- detect regressions automatically,
- compare prompt versions,
- compare model versions,
- evaluate retrieval quality,
- evaluate guardrail effectiveness,
- support CI/CD automation,
- enable reproducible experiments,
- support historical trend analysis,
- provide deployment quality gates.

---

# Evaluation Architecture

<CodeBlock language="text" content="Developer Change
    │
    ▼
Evaluation Runner
    │
    ▼
Benchmark Dataset
    │
    ▼
AI Pipeline
    │
    ▼
Guardrails
    │
    ▼
Metric Calculation
    │
    ▼
Evaluation Report
    │
    ▼
Quality Gate
    │
    ▼
Deployment Decision"/>

Evaluation occurs **before deployment** and may continue **after deployment** for monitoring.

---

# Evaluation Targets

Every major AI component is evaluated independently.

Current targets:

- JD Analyzer Agent
- Resume Analyzer Agent
- Planning Agent
- Retrieval Pipeline
- Rewrite Agent
- Guardrails Engine
- Validation Agent
- ATS Agent
- End-to-End Workflow

Each target has its own benchmark suite and thresholds.

---

# Benchmark Datasets

Tailr maintains multiple dataset types.

## Golden Dataset

Curated real-world examples with expected outputs.

Contents:

- canonical resumes,
- job descriptions,
- expected keywords,
- expected ATS improvements,
- expected structured outputs,
- expected validation outcomes.

The dataset is **version-controlled and immutable**.

---

## Synthetic Dataset

Programmatically generated edge cases.

Examples:

- missing sections,
- malformed LaTeX,
- conflicting dates,
- duplicate projects,
- prompt injection attempts,
- extremely long job descriptions.

Synthetic datasets improve coverage of rare scenarios.

---

## Regression Dataset

A frozen snapshot of previously passing cases used for release validation.

---

# Evaluation Types

## Prompt Evaluation

Measures:

- output quality,
- schema compliance,
- token usage,
- latency,
- guardrail pass rate.

---

## Model Evaluation

Compares:

- different LLMs,
- local vs cloud models,
- cost,
- accuracy,
- latency,
- structured output reliability.

---

## Retrieval Evaluation

Measures:

- Precision@K,
- Recall@K,
- MRR (Mean Reciprocal Rank),
- context relevance,
- retrieval latency,
- reranker effectiveness.

---

## Guardrail Evaluation

Measures:

- prompt injection detection rate,
- hallucination detection rate,
- JSON repair success rate,
- false positive rate,
- policy enforcement accuracy.

---

## Workflow Evaluation

Measures:

- workflow success rate,
- end-to-end latency,
- retry frequency,
- failure recovery rate,
- rendering success rate.

---

# Core Metrics

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Metric</Table.Cell><Table.Cell>Description</Table.Cell></Table.Row><Table.Row><Table.Cell>Precision@K</Table.Cell><Table.Cell>Retrieval accuracy</Table.Cell></Table.Row><Table.Row><Table.Cell>Recall@K</Table.Cell><Table.Cell>Relevant information retrieved</Table.Cell></Table.Row><Table.Row><Table.Cell>Faithfulness</Table.Cell><Table.Cell>Output grounded in retrieved context</Table.Cell></Table.Row><Table.Row><Table.Cell>Hallucination Rate</Table.Cell><Table.Cell>Unsupported generated content</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrail Pass Rate</Table.Cell><Table.Cell>Outputs passing all guardrails</Table.Cell></Table.Row><Table.Row><Table.Cell>ATS Improvement</Table.Cell><Table.Cell>Increase in ATS score</Table.Cell></Table.Row><Table.Row><Table.Cell>JSON Validity</Table.Cell><Table.Cell>Schema compliance</Table.Cell></Table.Row><Table.Row><Table.Cell>Token Usage</Table.Cell><Table.Cell>Cost efficiency</Table.Cell></Table.Row><Table.Row><Table.Cell>Latency</Table.Cell><Table.Cell>Response time</Table.Cell></Table.Row><Table.Row><Table.Cell>User Acceptance</Table.Cell><Table.Cell>Human approval rate</Table.Cell></Table.Row></Table>

---

# Quality Gates

Example thresholds:

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Metric</Table.Cell><Table.Cell align="end">Threshold</Table.Cell></Table.Row><Table.Row><Table.Cell>JSON Validity</Table.Cell><Table.Cell align="end">100%</Table.Cell></Table.Row><Table.Row><Table.Cell>Hallucination Rate</Table.Cell><Table.Cell align="end">< 1%</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrail Pass Rate</Table.Cell><Table.Cell align="end">≥ 99%</Table.Cell></Table.Row><Table.Row><Table.Cell>ATS Improvement</Table.Cell><Table.Cell align="end">≥ +10 points</Table.Cell></Table.Row><Table.Row><Table.Cell>Precision@5</Table.Cell><Table.Cell align="end">≥ 0.85</Table.Cell></Table.Row><Table.Row><Table.Cell>P95 Latency</Table.Cell><Table.Cell align="end">≤ 8s</Table.Cell></Table.Row></Table>

A deployment is blocked if any mandatory threshold fails.

---

# Evaluation Workflow

<CodeBlock language="text" content="Prompt / Model / Retrieval Change
         ↓
Execute Benchmark Suite
         ↓
Collect Metrics
         ↓
Compare Against Baseline
         ↓
Generate Evaluation Report
         ↓
Quality Gate Decision
         ↓
Approve or Reject"/>

The baseline is always the **current production configuration**.

---

# Regression Detection

Example:

<CodeBlock language="text" content="Production: prompt 1.2.0
ATS Improvement = +14

Candidate: prompt 1.3.0
ATS Improvement = +6

Regression detected
↓
Deployment blocked"/>

The framework prevents silent quality degradation.

---

# Evaluation Reports

Every evaluation stores:

- evaluation_id,
- benchmark_version,
- prompt_id,
- prompt_version,
- model_provider,
- model_name,
- embedding_model,
- reranker_model,
- workflow_version,
- metrics,
- execution_cost,
- timestamp,
- git commit SHA.

Reports are persisted in PostgreSQL for historical comparison.

---

# Prompt Registry Integration

Evaluations are linked to immutable prompt versions.

<CodeBlock language="text" content="resume_rewriter:1.2.0
     ↓
Evaluation #482
     ↓
Status: Passed
     ↓
Promoted to Production"/>

A prompt cannot be promoted unless a passing evaluation exists.

---

# Continuous Evaluation

Evaluations run:

- during local development,
- on pull requests,
- in CI pipelines,
- before releases,
- after model upgrades,
- after prompt changes,
- after retrieval changes,
- after guardrail changes,
- periodically in production.

Evaluation is **continuous**, not a one-time activity.

---

# Online Evaluation

Production workflows may be sampled for evaluation.

Sampled runs collect:

- user acceptance,
- guardrail outcomes,
- ATS deltas,
- latency,
- token usage,
- manual review feedback.

This detects real-world drift that offline benchmarks may miss.

---

# Human Review

Borderline evaluation results enter a review queue.

Human reviewers can:

- approve,
- reject,
- annotate failures,
- classify hallucinations,
- update benchmark expectations.

Human feedback is incorporated into future benchmark versions.

---

# Cost-Aware Evaluation

Evaluation budgets are enforced.

Strategies:

- smaller models for smoke tests,
- sampled datasets for PRs,
- full benchmark suites nightly,
- expensive cloud-model evaluations only for release candidates.

This keeps CI costs predictable.

---

# CI/CD Integration

<CodeBlock language="text" content="Git Push
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
Benchmark Report
↓
Deploy"/>

Deployment proceeds only if the evaluation stage passes.

---

# Observability

Evaluation telemetry integrates with:

- OpenTelemetry,
- Langfuse,
- Grafana,
- Prometheus,
- custom evaluation dashboards.

Tracked dimensions include:

- latency trends,
- token trends,
- hallucination trends,
- retrieval accuracy trends,
- prompt performance over time.

---

# Benchmark Versioning

Benchmarks are versioned independently.

Example:

<CodeBlock language="text" content="benchmarks/
├── v1.0/
├── v1.1/
└── v2.0/"/>

This allows historical evaluations to remain reproducible even as datasets evolve.

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

**Decision:** Rejected

---

## Option 2 — Unit Tests Only

### Advantages

- Fast execution
- Good for deterministic logic

### Disadvantages

- Cannot measure AI quality
- Does not detect prompt regressions
- Does not evaluate retrieval or guardrails

**Decision:** Rejected

---

## Option 3 — Evaluation-Driven Development

### Advantages

- Objective quality measurement
- Automated regression detection
- Continuous benchmarking
- Safer deployments
- Reproducible experiments
- Better model selection
- Guardrail validation

### Disadvantages

- Requires benchmark datasets
- Additional infrastructure
- Ongoing maintenance effort

**Decision:** Accepted

---

# Consequences

## Positive

- Higher AI reliability
- Reduced hallucinations
- Measurable improvements
- Safer prompt evolution
- Better model selection
- Continuous quality assurance
- Reproducible AI behavior

---

## Negative

- Benchmark maintenance overhead
- Longer CI execution times
- Increased storage for evaluation results
- Additional operational processes

---

# Risks

| Risk                         | Mitigation                           |
| ---------------------------- | ------------------------------------ |
| Benchmark bias               | Diverse datasets and periodic review |
| Dataset staleness            | Scheduled benchmark updates          |
| Metric overfitting           | Use multiple complementary metrics   |
| Evaluation cost              | Tiered evaluation strategy           |
| False confidence             | Include real production samples      |
| Human reviewer inconsistency | Review guidelines and calibration    |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
Workflow Engine
│
▼
AI Agents
│
▼
Prompt Registry
│
▼
LLM Router
│
▼
Guardrails
│
▼
Evaluation Pipeline
│
▼
Quality Gate
│
▼
Deployment"/>

The **Evaluation Pipeline acts as a mandatory quality gate** before production promotion.

---

# Future Enhancements

Planned enhancements include:

- automated benchmark generation,
- LLM-as-a-judge evaluation,
- pairwise ranking evaluation,
- retrieval drift detection,
- cost-performance optimization,
- reinforcement learning from human feedback,
- continuous prompt optimization,
- cross-model ensemble evaluation.

The current architecture is designed so these capabilities can be added incrementally.

---

# Related ADRs

- ADR-0005 — LlamaIndex as the AI Data and Workflow Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine
- ADR-0008 — LLM Router and Provider Abstraction Layer
- ADR-0009 — Prompt Registry with Immutable Versioning

---

# References

- testing.md
- validation-engine.md
- observability.md
- workflow-design.md
- evaluation-architecture.md
- guardrails-architecture.md

---

# Review Notes

This decision should be revisited if:

- deterministic AI techniques replace probabilistic generation,
- evaluation standards evolve significantly,
- external evaluation platforms become the primary quality gate,
- or operational overhead outweighs the benefits of continuous evaluation.

Until then, **Evaluation-Driven Development remains the standard methodology for AI quality assurance in Tailr**, ensuring measurable quality, automated regression detection, guardrail effectiveness, and safe evolution of prompts, models, and retrieval pipelines.

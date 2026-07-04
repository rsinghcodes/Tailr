# Agent Architecture

**Project:** Tailr

**Document Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the intelligent reasoning architecture of Tailr.

Unlike traditional AI applications that rely on a single LLM prompt, Tailr decomposes resume optimization into specialized reasoning agents coordinated through a workflow engine.

Each agent has a single responsibility and communicates using structured data models.

---

# 2. Design Philosophy

Tailr follows the principle:

> AI reasons. Software executes.

LLMs are responsible only for problems that require semantic understanding or language generation.

Deterministic software handles:

- Parsing
- Rendering
- Validation
- Storage
- Indexing
- Retrieval
- Compilation

This separation minimizes hallucinations and increases system reliability.

---

# 3. Workflow Overview

```

```

START
│
▼
Resume Parser (Software)
│
▼
Knowledge Builder (Software)
│
▼
JD Analyzer (AI)
│
▼
Planning Agent (AI)
│
▼
Rewrite Agent (AI)
│
▼
Validation Engine (Software)
│
▼
ATS Analysis Agent (AI)
│
▼
Renderer (Software)
│
▼
PDF Compiler (Software)
│
▼
END

```

---

# 4. Agent Communication

All agents communicate through typed Pydantic models.

Agents never exchange raw prompts or plain text.

Example

```

PlannerOutput

↓

RewriteInput

↓

RewriteOutput

↓

ValidationInput

````

This improves:

- reliability
- testing
- debugging
- observability

---

# 5. AI Agents

Tailr contains four primary AI agents.

| Agent | Responsibility |
|---------|---------------|
| JD Analyzer | Understand job descriptions |
| Planner | Decide what should change |
| Rewriter | Rewrite resume content |
| ATS Advisor | Explain ATS improvements |

---

# 6. JD Analyzer Agent

## Purpose

Convert an unstructured Job Description into structured requirements.

---

### Inputs

Job Description

---

### Outputs

```json
{
  "title": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "keywords": [],
  "soft_skills": []
}
````

---

### Responsibilities

Extract

- Job title
- Experience level
- Technical skills
- Preferred technologies
- Responsibilities
- Certifications
- Soft skills

---

### Constraints

Must never rewrite resumes.

Must never infer user experience.

---

### Success Criteria

- Accurate extraction
- Consistent schema
- High recall
- Deterministic JSON

---

# 7. Planning Agent

## Purpose

Determine how the resume should be optimized.

The planner never edits text.

It only creates an optimization strategy.

---

### Inputs

Canonical Resume

Job Requirement Model

Retrieved Knowledge

---

### Outputs

```json
{
  "summary": [],
  "skills": [],
  "experience": [],
  "projects": []
}
```

---

### Responsibilities

Decide

- sections to modify
- keywords to emphasize
- bullets to reorder
- projects to prioritize

---

### Forbidden Actions

- rewrite text
- invent skills
- fabricate projects
- modify dates

---

### Example

```
Projects

Move ResearchMind above ReadList

Reason

Agentic AI appears in JD
```

---

# 8. Rewrite Agent

## Purpose

Rewrite resume content according to the approved plan.

---

### Inputs

Resume Model

Rewrite Plan

Retrieved Context

---

### Outputs

Updated Resume Model

---

### Responsibilities

- improve readability
- strengthen action verbs
- improve ATS alignment
- preserve facts

---

### Constraints

Cannot

- invent employers
- invent projects
- invent metrics
- invent dates
- invent technologies

---

### Prompt Philosophy

Rewrite only.

Never reason about whether a section should change.

Planning has already happened.

---

# 9. ATS Advisor Agent

## Purpose

Explain optimization quality.

---

### Inputs

Original Resume

Optimized Resume

Job Requirements

---

### Outputs

```json
{
  "score": 91,
  "strengths": [],
  "weaknesses": [],
  "recommendations": []
}
```

---

### Responsibilities

Generate

- keyword coverage
- missing skills
- readability analysis
- ATS explanation

---

### Constraints

Cannot modify resumes.

---

# 10. Software Components

These are **not AI agents**.

---

## Resume Parser

Converts

LaTeX

↓

Canonical Resume Model

---

## Knowledge Builder

Creates

- embeddings
- chunks
- metadata
- vector indexes

---

## Hybrid Retriever

Performs

- dense retrieval
- sparse retrieval
- reranking

No LLM involved.

---

## Validation Engine

Checks

- hallucinations
- schema
- unsupported claims
- formatting
- business rules

---

## Renderer

Generates deterministic LaTeX.

---

## PDF Compiler

Compiles

resume.tex

↓

resume.pdf

---

# 11. Shared Memory

Agents communicate through a shared workflow state.

Example

```python
WorkflowState

resume

job_description

retrieved_chunks

rewrite_plan

rewritten_resume

validation

ats_report
```

Every agent reads only the fields it requires.

---

# 12. Context Window Strategy

Instead of sending the entire resume,

Tailr retrieves only relevant information.

```
Job Description

↓

Retriever

↓

Top 5 Resume Chunks

↓

Planner
```

Benefits

- lower cost
- lower latency
- higher accuracy

---

# 13. Failure Handling

Every agent defines explicit failure modes.

---

## JD Analyzer

Failure

Malformed JD

Recovery

Retry extraction

---

## Planner

Failure

Invalid JSON

Recovery

Retry with schema enforcement

---

## Rewriter

Failure

Hallucinated content

Recovery

Validation rejection

↓

Retry

---

## ATS Advisor

Failure

Incomplete report

Recovery

Regenerate explanation

---

# 14. Agent Boundaries

| Agent       | May Read      | May Modify            |
| ----------- | ------------- | --------------------- |
| JD Analyzer | JD            | Job Requirement Model |
| Planner     | Resume + JD   | Rewrite Plan          |
| Rewriter    | Resume + Plan | Resume Model          |
| ATS Advisor | Resume        | ATS Report            |

No agent may directly modify another agent's output.

---

# 15. Model Selection

Different reasoning tasks may use different models.

Example

| Task          | Model     |
| ------------- | --------- |
| JD Extraction | Qwen3 8B  |
| Planning      | Qwen3 14B |
| Rewriting     | Llama 3.1 |
| ATS Analysis  | Gemma 3   |

The architecture allows model replacement without changing workflows.

---

# 16. Prompt Contracts

Every AI agent follows the same contract.

## Objective

Single responsibility.

## Inputs

Typed schema.

## Constraints

Explicit rules.

## Output

Structured JSON.

## Validation

Schema validation before acceptance.

---

# 17. Observability

Each agent emits telemetry.

Metrics

- latency
- token usage
- retries
- success rate
- validation failures
- retrieval precision

These metrics are stored in Langfuse for monitoring and evaluation.

---

# 18. Human-in-the-Loop

The workflow pauses before rendering.

Users can

- accept changes
- reject changes
- edit manually
- regenerate individual sections

AI suggestions are never applied silently.

---

# 19. Future Agents

The architecture supports adding specialized agents.

Examples

- Cover Letter Agent
- LinkedIn Optimization Agent
- GitHub Portfolio Agent
- Career Coach Agent
- Interview Preparation Agent
- Salary Insights Agent
- Resume Reviewer Agent

Each integrates through the same workflow interface without changing existing agents.

---

# 20. Summary

Tailr uses a hybrid architecture where deterministic software components handle structured processing while AI agents perform semantic reasoning.

This separation improves correctness, observability, and maintainability while keeping hallucination risk low.

Every AI agent has:

- one responsibility
- typed inputs
- typed outputs
- explicit constraints
- measurable success criteria
- independent evaluation

The result is an agentic workflow that is modular, testable, and suitable for production systems.

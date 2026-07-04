# Workflow Design

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the execution workflow of Tailr.

It describes how requests move through the system, how components interact, how workflow state evolves, and how failures are handled.

Tailr uses an event-driven workflow orchestrated by **LlamaIndex Workflows**, where deterministic software components and AI agents collaborate through a shared workflow state.

---

# 2. Workflow Philosophy

Tailr follows several workflow principles.

## State Driven

The workflow revolves around a shared immutable state.

Each step consumes state.

Each step produces a new state.

---

## Event Driven

Every completed task emits an event.

Examples

```
ResumeParsed

KnowledgeIndexed

PlanningCompleted

RewriteCompleted

ValidationCompleted
```

---

## Deterministic Execution

Every workflow execution should produce reproducible results given identical:

- Resume
- Job Description
- Model
- Configuration

---

## Failure Isolation

Each workflow step can fail independently.

Failures do not corrupt previous states.

---

## Human Approval

Rendering only occurs after user approval.

---

# 3. High-Level Workflow

```
                  User Request
                        │
                        ▼
                 Upload Resume
                        │
                        ▼
                 Parse Resume
                        │
                        ▼
             Build Knowledge Index
                        │
                        ▼
             Upload Job Description
                        │
                        ▼
               Analyze Job Description
                        │
                        ▼
              Retrieve Relevant Context
                        │
                        ▼
                 Generate Rewrite Plan
                        │
                        ▼
                  Rewrite Resume
                        │
                        ▼
                 Validate Resume
                        │
                        ▼
                  Generate ATS Report
                        │
                        ▼
                  User Approval
                        │
                        ▼
                  Render LaTeX
                        │
                        ▼
                  Compile PDF
                        │
                        ▼
                  Store Version
                        │
                        ▼
                    Download
```

---

# 4. Workflow States

```
NEW

↓

PARSING

↓

INDEXING

↓

JD_ANALYSIS

↓

RETRIEVAL

↓

PLANNING

↓

REWRITING

↓

VALIDATING

↓

ATS_ANALYSIS

↓

AWAITING_APPROVAL

↓

RENDERING

↓

COMPILING

↓

COMPLETED
```

Failure may occur from any state.

---

# 5. Workflow State Object

Every step receives the same workflow state.

```python
WorkflowState

resume

job_description

resume_model

job_requirements

retrieved_chunks

rewrite_plan

rewritten_resume

validation_report

ats_report

render_result

status

errors
```

The workflow state is the single communication mechanism.

---

# 6. Step 1 — Resume Upload

Input

```
resume.tex
```

Actions

- Validate upload
- Store original file
- Emit ResumeUploaded

Output

```
UploadState
```

---

# 7. Step 2 — Resume Parsing

Input

```
resume.tex
```

Actions

- Parse LaTeX
- Build Canonical Resume Model
- Validate schema

Output

```
ResumeModel
```

Event

```
ResumeParsed
```

---

# 8. Step 3 — Knowledge Building

Actions

- Create semantic entities
- Generate chunks
- Generate embeddings
- Store vectors
- Build metadata

Output

```
Knowledge Store
```

Event

```
KnowledgeIndexed
```

---

# 9. Step 4 — Job Description Analysis

Input

```
Job Description
```

Actions

- Extract title
- Extract responsibilities
- Extract skills
- Extract keywords
- Normalize output

Output

```
JobRequirements
```

Event

```
JDAnalyzed
```

---

# 10. Step 5 — Retrieval

Actions

- Metadata filtering
- Dense retrieval
- BM25 retrieval
- Merge results
- Rerank
- Select Top-K

Output

```
RetrievedContext
```

Event

```
RetrievalCompleted
```

---

# 11. Step 6 — Planning

AI Agent

Planner

Input

- Resume
- Job Requirements
- Retrieved Context

Actions

- Decide sections to update
- Prioritize projects
- Reorder skills
- Recommend summary changes

Output

```
RewritePlan
```

Event

```
PlanningCompleted
```

---

# 12. Step 7 — Rewriting

AI Agent

Rewriter

Input

- Resume
- Rewrite Plan
- Retrieved Context

Actions

- Rewrite summary
- Rewrite bullets
- Improve wording

Constraints

- No hallucinations
- No invented facts

Output

```
UpdatedResume
```

Event

```
RewriteCompleted
```

---

# 13. Step 8 — Validation

Software Component

Validation Engine

Checks

- Schema
- Dates
- Companies
- Skills
- Metrics
- Formatting
- Hallucination

Output

```
ValidationReport
```

Decision

```
Pass

↓

Continue
```

or

```
Fail

↓

Retry Rewrite
```

---

# 14. Step 9 — ATS Analysis

AI Agent

ATS Advisor

Produces

- ATS Score
- Keyword Coverage
- Missing Keywords
- Recommendations

Output

```
ATSReport
```

---

# 15. Step 10 — User Review

User reviews

- Rewrite
- ATS Report
- Diff
- Suggestions

Options

```
Approve

Reject

Regenerate Section

Manual Edit
```

Rendering begins only after approval.

---

# 16. Step 11 — Rendering

Renderer

Converts

```
Resume Model

↓

LaTeX
```

No LLM involved.

---

# 17. Step 12 — PDF Compilation

Actions

```
latexmk

↓

PDF
```

Compilation logs are captured.

Output

```
resume.pdf
```

---

# 18. Step 13 — Version Storage

Persist

- Resume
- PDF
- ATS Report
- Rewrite Plan
- Diff
- Metadata

Future versions can be compared.

---

# 19. Event Flow

```
ResumeUploaded

↓

ResumeParsed

↓

KnowledgeIndexed

↓

JDAnalyzed

↓

RetrievalCompleted

↓

PlanningCompleted

↓

RewriteCompleted

↓

ValidationCompleted

↓

ATSGenerated

↓

ResumeApproved

↓

RenderingCompleted

↓

PDFCompiled

↓

OptimizationCompleted
```

---

# 20. Failure Handling

## Parser Failure

```
ResumeUploaded

↓

Parser Error

↓

Return Validation Error
```

---

## Retrieval Failure

```
Retry

↓

Fallback Retrieval

↓

Abort
```

---

## Planner Failure

```
Retry

↓

Different Model

↓

Abort
```

---

## Rewrite Failure

Validation detects hallucination.

```
Rewrite

↓

Validation Failed

↓

Retry
```

Maximum retry count is configurable.

---

## Rendering Failure

```
Compilation Error

↓

Display Logs

↓

Manual Fix
```

---

# 21. Parallel Execution

Future workflow versions may execute independent tasks concurrently.

Example

```
Resume Parsing
             \
              \
               ---> Knowledge Index
              /
JD Analysis  /
```

Possible parallel tasks

- Embedding generation
- ATS preprocessing
- Resume statistics
- Resume diff generation

---

# 22. Checkpointing

Every workflow state is persisted.

Benefits

- Resume execution
- Retry failed steps
- Workflow replay
- Debugging

Checkpoints include

- Input
- Output
- Execution time
- Tokens
- Errors

---

# 23. Observability

Every step records

- latency
- retries
- token usage
- model
- retrieval quality
- validation failures

These metrics are exported to Langfuse.

---

# 24. Workflow Diagram

```
User

↓

Upload

↓

Parse

↓

Knowledge Build

↓

JD Analysis

↓

Retrieve

↓

Plan

↓

Rewrite

↓

Validate

↓

ATS Analysis

↓

User Review

↓

Render

↓

Compile

↓

Store

↓

Download
```

---

# 25. Future Workflow Extensions

The workflow engine supports additional pipelines.

Examples

- Cover Letter Workflow
- LinkedIn Optimization Workflow
- Portfolio Workflow
- GitHub Analysis Workflow
- Interview Preparation Workflow

Each workflow reuses:

- Knowledge Layer
- Retrieval Layer
- Validation Layer
- Rendering Layer

Only the planning and generation stages change.

---

# 26. Summary

Tailr's workflow is an event-driven, state-based orchestration built on LlamaIndex Workflows.

Rather than chaining prompts together, the system progresses through deterministic stages where AI agents perform semantic reasoning while software components handle parsing, validation, rendering, and persistence.

This architecture enables reliable retries, comprehensive observability, human approval, and future extensibility while maintaining a clear separation between reasoning and execution.

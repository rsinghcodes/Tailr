# Workflow Design

**Project:** Tailr

**Version:** 1.1

**Status:** Draft

---

# 1. Purpose

This document defines the execution workflow of Tailr.

It describes how requests move through the system, how components interact, how workflow state evolves, and how failures are handled.

Tailr uses an event-driven workflow orchestrated by **LlamaIndex Workflows**, where deterministic software components and AI agents collaborate through a shared workflow state.

The workflow is designed to be:

- deterministic
- observable
- recoverable
- auditable
- scalable
- human-supervised

---

# 2. Workflow Philosophy

Tailr follows several workflow principles.

## State Driven

The workflow revolves around a shared immutable state.

Each step consumes state.

Each step produces a new state.

No component mutates previous state directly.

---

## Event Driven

Every completed task emits an event.

Examples

```text
ResumeParsed

KnowledgeIndexed

PlanningCompleted

RewriteCompleted

GuardrailsCompleted

ValidationCompleted
```

Events are persisted for replay, debugging, and audit purposes.

---

## Deterministic Execution

Every workflow execution should produce reproducible results given identical:

- Resume
- Job Description
- Model
- Prompt Version
- Configuration

Determinism is critical for debugging and evaluation.

---

## Failure Isolation

Each workflow step can fail independently.

Failures do not corrupt previous states.

Retries occur at the step level rather than restarting the entire workflow.

---

## Human Approval

Rendering only occurs after user approval.

AI suggestions are never applied silently.

---

## Guardrail First

Every AI-generated artifact passes through deterministic Guardrail policies before validation.

Guardrails enforce:

- immutable fact protection
- schema compliance
- business policies
- prompt security
- output safety

Only Guardrail-approved outputs continue through the workflow.

---

# 3. High-Level Workflow

```text
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
                Execute Guardrails
                        │
                        ▼
                 Validate Resume
                        │
                        ▼
                  Generate ATS Report
                        │
                        ▼
                  Human Approval
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

```text
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

GUARDRAILS

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

Failed workflows transition to:

```text
FAILED
```

Cancelled workflows transition to:

```text
CANCELLED
```

---

# 5. Workflow State Object

Every step receives the same workflow state.

```python
WorkflowState

request_id

workflow_id

resume

job_description

resume_model

job_requirements

retrieved_chunks

rewrite_plan

rewritten_resume

guardrail_report

validation_report

ats_report

render_result

telemetry

status

retry_count

errors
```

Additional metadata:

```python
telemetry

started_at

updated_at

current_step

step_history

token_usage

latency_ms

model_versions

prompt_versions
```

The workflow state is the single communication mechanism between all components.

---

# 6. Step 1 — Resume Upload

**Input**

```text
resume.tex
```

**Actions**

- Validate upload
- Validate MIME type
- Validate file size
- Store original file
- Generate `request_id`
- Generate `workflow_id`
- Emit `ResumeUploaded`

**Output**

```text
UploadState
```

**Event**

```text
ResumeUploaded
```

---

# 7. Step 2 — Resume Parsing

**Input**

```text
resume.tex
```

**Actions**

- Parse LaTeX
- Build Canonical Resume Model
- Normalize entities
- Validate schema
- Extract metadata

**Output**

```text
ResumeModel
```

**Event**

```text
ResumeParsed
```

---

# 8. Step 3 — Knowledge Building

**Actions**

- Create semantic entities
- Generate chunks
- Generate embeddings
- Store vectors
- Build metadata
- Update knowledge graph

**Output**

```text
KnowledgeStore
```

**Event**

```text
KnowledgeIndexed
```

---

# 9. Step 4 — Job Description Analysis

**Input**

```text
Job Description
```

**Actions**

- Extract title
- Extract responsibilities
- Extract required skills
- Extract preferred skills
- Extract keywords
- Normalize output
- Validate structured schema

**Output**

```text
JobRequirements
```

**Event**

```text
JDAnalyzed
```

---

# 10. Step 5 — Retrieval

**Actions**

- Intent detection
- Metadata filtering
- Dense retrieval
- BM25 retrieval
- Merge results
- Rerank candidates
- Select Top-K
- Build deterministic context package

**Output**

```text
RetrievedContext
```

**Event**

```text
RetrievalCompleted
```

The context package contains:

- retrieved chunks
- similarity scores
- rerank scores
- citations
- retrieval rationale

## 11. Step 6 — Planning

**AI Agent:** Planner

### Input

- Resume
- Job Requirements
- Retrieved Context

### Actions

- Decide sections to update
- Prioritize projects
- Reorder skills
- Recommend summary changes
- Select evidence-backed highlights
- Generate rationale for each proposed change

### Constraints

- No rewriting
- No invented facts
- No modification of immutable entities
- Must cite retrieved evidence

### Output

```text
RewritePlan
```

### Event

```text
PlanningCompleted
```

---

## 12. Step 7 — Rewriting

**AI Agent:** Rewriter

### Input

- Resume
- Rewrite Plan
- Retrieved Context

### Actions

- Rewrite summary
- Rewrite experience bullets
- Improve wording
- Improve ATS alignment
- Preserve factual content
- Attach evidence citations

### Constraints

- No hallucinations
- No invented employers
- No invented projects
- No invented metrics
- No invented dates
- No invented technologies

### Output

```text
UpdatedResume
```

### Event

```text
RewriteCompleted
```

---

## 13. Step 8 — Guardrail Evaluation

**Software Component:** Guardrails Engine

### Purpose

Validate AI-generated content before business validation.

### Checks

- Immutable fact protection
- Schema compliance
- Prohibited modifications
- Business policy enforcement
- Prompt injection artifacts
- Prompt leakage
- Unsupported claims
- PII leakage
- ATS formatting constraints

### Output

```text
GuardrailReport
```

### Decision

```text
Pass

↓

Validation
```

or

```text
Fail

↓

Repair Attempt

↓

Retry Rewrite
```

### Repair Strategy

The Guardrails Engine may automatically:

- repair malformed JSON
- remove unsupported fields
- normalize formatting
- sanitize unsafe output

If repair fails, the workflow is rejected and returned for regeneration.

### Event

```text
GuardrailsStarted

↓

GuardrailsCompleted
```

---

## 14. Step 9 — Validation

**Software Component:** Validation Engine

Validation assumes all Guardrail policies have already been satisfied.

### Checks

- Schema consistency
- Date consistency
- Company consistency
- Technology consistency
- Metric validation
- Formatting rules
- Citation coverage
- Cross-entity consistency
- Business rule compliance

### Output

```text
ValidationReport
```

### Decision

```text
Pass

↓

Continue
```

or

```text
Fail

↓

Retry Rewrite
```

### Event

```text
ValidationCompleted
```

---

## 15. Step 10 — ATS Analysis

**AI Agent:** ATS Advisor

### Produces

- ATS Score
- Keyword Coverage
- Missing Keywords
- Readability Analysis
- Section Ordering Feedback
- Improvement Recommendations

### Output

```text
ATSReport
```

The ATS Advisor only analyzes validated resumes and never modifies workflow state.

### Event

```text
ATSGenerated
```

---

## 16. Step 11 — Human Review

The user reviews:

- rewritten resume
- ATS report
- guardrail report
- validation report
- workflow diff
- AI reasoning summary

### Available Actions

```text
Approve

Reject

Regenerate Section

Manual Edit

Request Different Tone
```

### Approval Rules

- approval is mandatory before rendering
- approvals are auditable
- reviewer identity is recorded
- timestamp is recorded

### Event

```text
ResumeApproved
```

---

## 17. Step 12 — Rendering

**Software Component:** Renderer

Converts:

```text
Resume Model

↓

LaTeX
```

### Characteristics

- deterministic
- template-driven
- no LLM involvement
- reproducible output
- schema-aware rendering

### Output

```text
RenderResult
```

### Event

```text
RenderingCompleted
```

---

## 18. Step 13 — PDF Compilation

### Actions

```text
latexmk

↓

PDF
```

### Additional Steps

- capture compilation logs
- detect LaTeX errors
- verify PDF generation
- compute checksum
- store artifact metadata

### Output

```text
resume.pdf
```

### Event

```text
PDFCompiled
```

## 19. Step 14 — Version Storage

The final approved version is persisted.

### Persisted Artifacts

- Canonical Resume
- Optimized Resume
- LaTeX source
- PDF artifact
- ATS Report
- Guardrail Report
- Validation Report
- Rewrite Plan
- Workflow Diff
- Retrieval Citations
- Prompt Version
- Model Version
- Workflow Metadata
- Trace ID

### Storage Locations

```text id=

```

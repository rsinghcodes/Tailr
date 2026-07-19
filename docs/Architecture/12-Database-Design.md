# Database Design

**Project:** Tailr

**Version:** 1.1

**Status:** Draft

---

# 1. Purpose

This document defines the persistence architecture for Tailr.

The platform stores several fundamentally different categories of information, including structured business data, semantic embeddings, workflow state, generated artifacts, AI telemetry, and guardrail validation events.

Rather than forcing all data into a single database, Tailr uses a polyglot persistence architecture where each storage technology is selected according to its strengths.

---

# 2. Design Goals

The persistence layer must:

- Preserve resume history
- Support semantic retrieval
- Store workflow checkpoints
- Enable fast searches
- Maintain referential integrity
- Support future scaling
- Minimize operational complexity
- Provide auditability for AI-generated content
- Store guardrail validation outcomes

---

# 3. Database Architecture

```text
                     Tailr Backend
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
 PostgreSQL            Qdrant              Redis
      │                    │                    │
Structured Data      Vector Search       Cache & Workflow
      │
      ▼
 Object Storage
(.tex, PDFs, Reports)
```

---

# 4. Storage Responsibilities

| Storage        | Purpose                           |
| -------------- | --------------------------------- |
| PostgreSQL     | Business data and audit logs      |
| Qdrant         | Embeddings and semantic retrieval |
| Redis          | Cache, workflow state, queues     |
| Object Storage | Resume files, PDFs, reports       |

---

# 5. PostgreSQL Schema

Core tables

```text
users
resumes
resume_versions
job_descriptions
workflow_runs
ats_reports
feedback
optimization_history
guardrail_events
projects
skills
```

---

# 6. Entity Relationship Diagram

```text
User
 │
 ├── Resume
 │      │
 │      ├── ResumeVersion
 │      │       │
 │      │       ├── ATSReport
 │      │       └── GuardrailEvent
 │      │
 │      └── OptimizationHistory
 │
 ├── JobDescription
 │
 ├── WorkflowRun
 │       │
 │       └── GuardrailEvent
 │
 └── Feedback
```

---

# 7. Users Table

```text
users

id UUID PK
email
name
created_at
updated_at
```

Version 1 may support a single local user.

Authentication can be introduced later without changing the schema.

---

# 8. Resumes Table

```text
resumes

id
user_id
title
current_version
status
created_at
updated_at
```

Each resume acts as a logical container.

---

# 9. Resume Versions

```text
resume_versions

id
resume_id
version
latex_path
pdf_path
canonical_json
created_at
```

Each optimization creates a new immutable version.

---

# 10. Job Descriptions

```text
job_descriptions

id
company
title
description
parsed_requirements
created_at
```

Parsed requirements are stored as JSONB.

---

# 11. Workflow Runs

```text
workflow_runs

id
resume_id
job_description_id
status
current_step
started_at
completed_at
token_usage
latency_ms
```

Supports resumable workflows.

---

# 12. ATS Reports

```text
ats_reports

id
resume_version_id
overall_score
dimension_scores
recommendations
created_at
```

Dimension scores are stored as JSONB.

---

# 13. Feedback

```text
feedback

id
workflow_id
accepted
comment
created_at
```

User feedback becomes training data for future improvements.

---

# 14. Optimization History

```text
optimization_history

id
resume_id
job_description_id
ats_before
ats_after
execution_time
created_at
```

Supports historical analytics.

---

# 15. Guardrail Events

The Guardrails layer produces structured audit events for every AI interaction.

```text
guardrail_events

id UUID PK
workflow_run_id UUID FK
resume_version_id UUID FK NULL
request_id VARCHAR(64)
validator_name VARCHAR(100)
status VARCHAR(20)
severity VARCHAR(20)
repaired BOOLEAN
violations JSONB
metadata JSONB
latency_ms INTEGER
created_at TIMESTAMP
```

### Status Values

- passed
- repaired
- rejected
- skipped
- error

### Severity Values

- low
- medium
- high
- critical

### Example Violations

```json
["prompt_injection_detected", "hallucinated_company", "invalid_json_schema"]
```

This table provides:

- AI auditability
- Security monitoring
- Hallucination tracking
- Prompt injection detection
- Output repair analytics
- Compliance reporting

---

# 16. JSONB Usage

PostgreSQL JSONB stores semi-structured AI data.

Examples

```text
parsed_requirements
rewrite_plan
validation_report
ats_breakdown
prompt_metadata
guardrail_metadata
hallucination_report
pii_detection_report
```

Frequently queried fields should remain relational.

---

# 17. Qdrant Collections

```text
resume_chunks
projects
experience
skills
career_guides
job_descriptions
feedback
```

Each collection stores vectors plus metadata.

---

# 18. Vector Metadata

Example

```json
{
  "entity_type": "Project",
  "entity_id": "proj_123",
  "category": "AI",
  "technologies": ["LangChain", "FastAPI"],
  "importance": 0.95
}
```

Metadata supports hybrid retrieval.

---

# 19. Redis Usage

Redis stores transient data only.

Examples

```text
Workflow state
Prompt cache
Embedding cache
Rate limits
Session cache
Task queue
Progress updates
Guardrail temporary state
Output repair cache
```

Persistent business data never resides exclusively in Redis.

---

# 20. Object Storage

Stored artifacts include:

- Original LaTeX
- Generated LaTeX
- PDFs
- Validation reports
- Guardrail reports
- Diff reports
- Logs

Suggested structure

```text
storage/
  resumes/
  versions/
  pdf/
  reports/
  guardrails/
  logs/
```

---

# 21. Indexing Strategy

### PostgreSQL Indexes

```text
users.email
resumes.user_id
workflow_runs.status
job_descriptions.company
resume_versions.resume_id
guardrail_events.workflow_run_id
guardrail_events.request_id
guardrail_events.validator_name
guardrail_events.status
guardrail_events.created_at
```

### GIN Indexes

```text
parsed_requirements
validation_report
dimension_scores
violations
metadata
```

Qdrant indexes vectors automatically.

---

# 22. Transactions

Transactional operations include:

- Resume creation
- Version creation
- Workflow completion
- ATS report persistence
- Guardrail event persistence

Database transactions prevent partial writes and ensure audit consistency.

---

# 23. Data Retention

Policies

- Workflow logs: 90 days
- Guardrail events: 180 days
- Cache: 24 hours
- Resume versions: retained
- PDFs: retained
- ATS reports: retained
- Feedback: retained

Retention policies are configurable.

---

# 24. Backup Strategy

### PostgreSQL

- Daily full backup
- Hourly WAL archiving
- Guardrail audit tables included

### Qdrant

- Snapshot collections

### Object Storage

- Incremental backups

### Redis

- No backup required (cache only)

---

# 25. Migration Strategy

Database schema evolves using Alembic.

Every migration includes:

- `upgrade()`
- `downgrade()`

Schema versions are tracked in source control.

Guardrail schema changes must remain backward compatible whenever possible.

---

# 26. Security

Sensitive data protections include:

- Encryption at rest
- TLS in transit
- Parameterized SQL
- Least-privilege database roles
- Signed object URLs
- Secure file permissions
- Audit logging for AI safety events
- PII detection before persistence
- Guardrail event access restricted to administrators

Raw LLM prompts and outputs should not be stored unless explicitly enabled for debugging.

---

# 27. Performance Targets

Target metrics

| Metric                      | Target  |
| --------------------------- | ------- |
| Resume retrieval            | <50 ms  |
| Workflow lookup             | <20 ms  |
| ATS report lookup           | <30 ms  |
| Vector search               | <100 ms |
| Cache lookup                | <5 ms   |
| Guardrail validation lookup | <15 ms  |

---

# 28. Scaling Strategy

### PostgreSQL

- Read replicas
- Connection pooling
- Table partitioning for `guardrail_events`

### Qdrant

- Distributed collections

### Redis

- Cluster mode

### Object Storage

- S3-compatible backend

The application layer remains unchanged.

---

# 29. Monitoring

Database metrics

- Query latency
- Slow queries
- Cache hit ratio
- Connection count
- Storage usage
- Vector search latency
- Workflow throughput
- Guardrail rejection rate
- Prompt injection detection count
- Hallucination detection count
- Output repair success rate

Metrics integrate with Grafana and Prometheus.

---

# 30. Future Tables

Future schema additions

- applications
- cover_letters
- github_repositories
- linkedin_profiles
- interviews
- recruiter_feedback
- portfolios
- career_goals
- ai_evaluations
- prompt_versions
- model_benchmarks

The schema is designed to accommodate these without major restructuring.

---

# 31. Architecture Decisions

| Decision                        | Rationale                                |
| ------------------------------- | ---------------------------------------- |
| PostgreSQL                      | ACID transactions and JSONB support      |
| Qdrant                          | High-performance semantic retrieval      |
| Redis                           | Fast ephemeral state and caching         |
| Object storage                  | Efficient binary artifact storage        |
| JSONB                           | Flexible AI metadata                     |
| Immutable resume versions       | Auditability and rollback                |
| Guardrail event table           | AI safety auditability and observability |
| Provider-independent guardrails | Consistent validation across all LLMs    |

---

# 32. Summary

Tailr adopts a polyglot persistence architecture that separates transactional, semantic, transient, binary, and AI safety data into specialized storage systems.

By combining PostgreSQL, Qdrant, Redis, and object storage, the platform achieves:

- strong consistency for business data
- efficient semantic search
- fast workflow execution
- scalable artifact management
- auditable AI safety validation
- guardrail observability and compliance reporting

The introduction of the `guardrail_events` table provides a complete audit trail for AI-generated content, enabling hallucination tracking, prompt injection monitoring, output repair analytics, and future compliance requirements.

This architecture supports both the current resume optimization workflow and future expansion into a comprehensive **Career Intelligence Platform** with enterprise-grade AI governance.

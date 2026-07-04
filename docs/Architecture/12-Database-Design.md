# Database Design

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the persistence architecture for Tailr.

The platform stores several fundamentally different categories of information, including structured business data, semantic embeddings, workflow state, generated artifacts, and AI telemetry.

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

---

# 3. Database Architecture

```
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

| Storage        | Purpose                       |
| -------------- | ----------------------------- |
| PostgreSQL     | Business data                 |
| Qdrant         | Embeddings and retrieval      |
| Redis          | Cache, workflow state, queues |
| Object Storage | Resume files, PDFs, reports   |

---

# 5. PostgreSQL Schema

Core tables

```
users

resumes

resume_versions

job_descriptions

workflow_runs

ats_reports

feedback

optimization_history

projects

skills
```

---

# 6. Entity Relationship Diagram

```
User
 │
 ├── Resume
 │      │
 │      ├── ResumeVersion
 │      │
 │      └── ATSReport
 │
 ├── JobDescription
 │
 ├── WorkflowRun
 │
 └── OptimizationHistory
```

---

# 7. Users Table

```
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

```
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

```
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

```
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

```
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

```
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

```
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

```
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

# 15. JSONB Usage

PostgreSQL JSONB stores semi-structured AI data.

Examples

```
parsed_requirements

rewrite_plan

validation_report

ats_breakdown

prompt_metadata
```

Frequently queried fields should remain relational.

---

# 16. Qdrant Collections

```
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

# 17. Vector Metadata

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

# 18. Redis Usage

Redis stores transient data only.

Examples

```
Workflow state

Prompt cache

Embedding cache

Rate limits

Session cache

Task queue

Progress updates
```

Persistent business data never resides exclusively in Redis.

---

# 19. Object Storage

Stored artifacts include:

- Original LaTeX
- Generated LaTeX
- PDFs
- Validation reports
- Diff reports
- Logs

Suggested structure

```
storage/

resumes/

versions/

pdf/

reports/

logs/
```

---

# 20. Indexing Strategy

PostgreSQL indexes

```
users.email

resumes.user_id

workflow_runs.status

job_descriptions.company

resume_versions.resume_id
```

GIN indexes

```
parsed_requirements

validation_report

dimension_scores
```

Qdrant indexes vectors automatically.

---

# 21. Transactions

Transactional operations include:

- Resume creation
- Version creation
- Workflow completion
- ATS report persistence

Database transactions prevent partial writes.

---

# 22. Data Retention

Policies

- Workflow logs: 90 days
- Cache: 24 hours
- Resume versions: retained
- PDFs: retained
- ATS reports: retained
- Feedback: retained

Retention policies are configurable.

---

# 23. Backup Strategy

PostgreSQL

- Daily full backup
- Hourly WAL archiving

Qdrant

- Snapshot collections

Object Storage

- Incremental backups

Redis

- No backup required (cache only)

---

# 24. Migration Strategy

Database schema evolves using Alembic.

Every migration includes:

- upgrade()
- downgrade()

Schema versions are tracked in source control.

---

# 25. Security

Sensitive data protections include:

- Encryption at rest
- TLS in transit
- Parameterized SQL
- Least-privilege database roles
- Signed object URLs
- Secure file permissions

---

# 26. Performance Targets

Target metrics

| Metric            | Target  |
| ----------------- | ------- |
| Resume retrieval  | <50 ms  |
| Workflow lookup   | <20 ms  |
| ATS report lookup | <30 ms  |
| Vector search     | <100 ms |
| Cache lookup      | <5 ms   |

---

# 27. Scaling Strategy

Future scaling

PostgreSQL

- Read replicas
- Connection pooling

Qdrant

- Distributed collections

Redis

- Cluster mode

Object Storage

- S3-compatible backend

The application layer remains unchanged.

---

# 28. Monitoring

Database metrics

- Query latency
- Slow queries
- Cache hit ratio
- Connection count
- Storage usage
- Vector search latency
- Workflow throughput

Metrics integrate with Grafana and Prometheus.

---

# 29. Future Tables

Future schema additions

- applications
- cover_letters
- github_repositories
- linkedin_profiles
- interviews
- recruiter_feedback
- portfolios
- career_goals

The schema is designed to accommodate these without major restructuring.

---

# 30. Architecture Decisions

| Decision                  | Rationale                           |
| ------------------------- | ----------------------------------- |
| PostgreSQL                | ACID transactions and JSONB support |
| Qdrant                    | High-performance semantic retrieval |
| Redis                     | Fast ephemeral state and caching    |
| Object storage            | Efficient binary artifact storage   |
| JSONB                     | Flexible AI metadata                |
| Immutable resume versions | Auditability and rollback           |

---

# 31. Summary

Tailr adopts a polyglot persistence architecture that separates transactional, semantic, transient, and binary data into specialized storage systems.

By combining PostgreSQL, Qdrant, Redis, and object storage, the platform achieves strong consistency for business data, efficient semantic search, fast workflow execution, and scalable artifact management.

This architecture supports both the current resume optimization workflow and future expansion into a comprehensive Career Intelligence Platform.

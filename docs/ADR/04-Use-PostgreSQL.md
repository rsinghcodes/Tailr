# ADR-0004: Use PostgreSQL as the Primary Database

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr manages several categories of persistent data:

- Users
- Resume metadata
- Resume versions
- Job descriptions
- AI workflows
- Prompt versions
- Validation reports
- ATS evaluations
- Audit logs
- System configuration

These datasets require:

- ACID transactions
- Referential integrity
- Strong consistency
- Complex queries
- Version history
- Flexible metadata storage
- Future scalability

The platform therefore requires a production-grade relational database.

---

# Decision

Tailr will use **PostgreSQL** as its primary database.

PostgreSQL stores all transactional and relational data.

The database is responsible for:

- User management
- Resume metadata
- Workflow state
- Version history
- Prompt versions
- Evaluation results
- Audit records
- Configuration

Large documents and embeddings are stored outside PostgreSQL.

---

# Decision Drivers

The selected database must provide:

- ACID compliance
- Strong consistency
- Excellent indexing
- Mature ecosystem
- Flexible schema support
- Reliable migrations
- High performance
- Open-source licensing

---

# Why PostgreSQL?

PostgreSQL provides:

- Mature relational engine
- Excellent query optimizer
- JSONB support
- Full-text search
- Extensions
- Reliable transactions
- Strong Python ecosystem

Unlike document databases, PostgreSQL allows strict relationships while still supporting semi-structured AI metadata.

---

# Data Responsibilities

PostgreSQL stores:

```
Users

↓

Resumes

↓

Resume Versions

↓

Workflow Metadata

↓

Prompt Versions

↓

Validation Reports

↓

ATS Results

↓

Audit Logs
```

Embeddings remain outside PostgreSQL.

---

# JSONB Usage

Certain entities require flexible metadata.

Example:

```json
{
  "model": "qwen3:8b",
  "temperature": 0.3,
  "tokens": 1542,
  "latency_ms": 3120,
  "prompt_version": "v5"
}
```

Using JSONB allows new metadata fields without frequent schema migrations.

---

# Schema Strategy

Tailr uses a normalized schema.

Example entities:

- users
- resumes
- resume_versions
- job_descriptions
- workflows
- prompts
- evaluations
- audit_logs

Relationships are enforced using foreign keys.

---

# Transactions

Critical operations execute within transactions.

Example:

```
Create Resume Version

↓

Store Workflow

↓

Store Validation Report

↓

Store ATS Score

↓

Commit
```

Either all records are committed or none are.

---

# Migrations

Database schema changes are managed with:

```
Alembic
```

Benefits:

- Version-controlled schema
- Rollback support
- Reproducible deployments

---

# Indexing Strategy

Indexes will be created for:

- user_id
- workflow_id
- resume_id
- created_at
- updated_at
- status

Additional indexes are added based on query profiling.

---

# Alternatives Considered

## Option 1 — MongoDB

### Advantages

- Flexible schema
- Easy document storage

### Disadvantages

- Weak relational modeling
- Complex joins
- Less suitable for transactional workflows

Decision: Rejected

---

## Option 2 — SQLite

### Advantages

- Simple setup
- Lightweight
- Ideal for local prototypes

### Disadvantages

- Limited concurrency
- Not suitable for production
- Poor horizontal scalability

Decision: Rejected

---

## Option 3 — MySQL

### Advantages

- Mature ecosystem
- Good performance

### Disadvantages

- Less capable JSON support
- Fewer advanced features for AI metadata
- Smaller extension ecosystem

Decision: Rejected

---

## Option 4 — PostgreSQL

### Advantages

- ACID compliant
- JSONB support
- Excellent indexing
- Strong ecosystem
- Proven production reliability
- Rich extension support

### Disadvantages

- More operational complexity than SQLite
- Slightly steeper learning curve

Decision: Accepted

---

# Consequences

## Positive

- Reliable transactions
- Strong consistency
- Flexible JSONB storage
- Excellent reporting queries
- Easy schema evolution
- Mature tooling

---

## Negative

- Requires migration management
- Additional operational overhead
- Larger resource footprint than SQLite

---

# Risks

| Risk                   | Mitigation                             |
| ---------------------- | -------------------------------------- |
| Poor query performance | Proper indexing and query optimization |
| Schema evolution       | Versioned Alembic migrations           |
| Large JSON fields      | Store only metadata in JSONB           |
| Database growth        | Partitioning and archival strategies   |

---

# Architecture Integration

```
                FastAPI
                   │
                   ▼
          Application Layer
                   │
                   ▼
        Repository Interfaces
          ┌────────┴────────┐
          ▼                 ▼
    PostgreSQL         Qdrant
 (Transactional)   (Vector Search)
```

PostgreSQL and Qdrant have distinct responsibilities.

---

# Data Ownership

| Component          | Storage        |
| ------------------ | -------------- |
| Users              | PostgreSQL     |
| Resume Metadata    | PostgreSQL     |
| Resume Versions    | PostgreSQL     |
| Workflow State     | PostgreSQL     |
| Prompt Metadata    | PostgreSQL     |
| Validation Reports | PostgreSQL     |
| ATS Results        | PostgreSQL     |
| Embeddings         | Qdrant         |
| Generated PDFs     | Object Storage |

This separation prevents misuse of the relational database for vector search.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture
- ADR-0003 — Use FastAPI as the Primary Backend Framework
- ADR-0005 — Use Qdrant as the Vector Database
- ADR-0006 — Use LlamaIndex for RAG

---

# References

- Database-Design.md
- Data-Models.md
- API-Specification.md
- Deployment.md

---

# Review Notes

This decision should be revisited if:

- workload characteristics become predominantly analytical,
- a distributed SQL database becomes necessary,
- or application scale exceeds the operational capabilities of a single PostgreSQL instance.

Until then, PostgreSQL remains the authoritative transactional data store for Tailr.

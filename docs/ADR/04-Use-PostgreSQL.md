# ADR-0004: Use PostgreSQL as the Primary Transactional Database

**Status:** Accepted

**Date:** 2026-07-20

**Authors:** Tailr Engineering

---

# Context

Tailr manages multiple categories of persistent data:

- Users
- Canonical resumes
- Resume versions
- Job descriptions
- Optimization plans
- AI workflows
- Workflow state transitions
- Prompt versions
- Validation results
- Guardrail events
- ATS evaluations
- Generated artifacts
- Audit logs
- System configuration
- Evaluation metadata

These datasets require:

- ACID transactions
- Referential integrity
- Strong consistency
- Complex relational queries
- Immutable version history
- Flexible metadata storage
- Auditability
- Future scalability

The platform therefore requires a production-grade relational database capable of serving as the authoritative transactional store.

---

# Decision

Tailr will use **PostgreSQL** as its primary transactional database.

PostgreSQL stores all **relational and workflow metadata**.

The database is responsible for:

- User management
- Canonical resume metadata
- Resume version history
- Workflow state
- Workflow transitions
- Prompt metadata and versions
- Validation results
- Guardrail audit events
- ATS reports
- Generated artifact metadata
- Evaluation metadata
- Audit records
- System configuration

Large binary artifacts and vector embeddings are stored outside PostgreSQL.

---

# Decision Drivers

The selected database must provide:

- ACID compliance
- Strong consistency
- Excellent indexing
- Mature ecosystem
- Flexible schema support
- Reliable migrations
- High concurrency
- Open-source licensing
- Rich JSON capabilities
- Proven production reliability

---

# Why PostgreSQL?

PostgreSQL provides:

- Mature relational engine
- Excellent query optimizer
- JSONB support
- Full-text search
- Window functions
- Materialized views
- Extensions ecosystem
- Reliable transactions
- Strong Python tooling
- Native UUID support

Unlike document databases, PostgreSQL allows strict relationships while still supporting semi-structured AI metadata through JSONB.

---

# Data Responsibilities

PostgreSQL stores:

<CodeBlock language="text" content="Users
↓
Canonical Resumes
↓
Resume Versions
↓
Optimization Plans
↓
Workflows
↓
Workflow States
↓
Validation Results
↓
Guardrail Events
↓
ATS Results
↓
Generated Artifact Metadata
↓
Audit Logs"/>

Embeddings remain outside PostgreSQL and are stored in **Qdrant Cloud**.

---

# JSONB Strategy

Certain entities require flexible metadata.

Example:

<CodeBlock language="json" content="{
"model": "qwen3:8b",
"temperature": 0.3,
"tokens": 1542,
"latency_ms": 3120,
"prompt_version": "v5",
"retrieval_k": 8,
"reranker": "bge-reranker-v2"
}"/>

JSONB allows new metadata fields to be added without frequent schema migrations while preserving queryability.

Guidelines:

- **Structured business data → relational columns**
- **Variable AI metadata → JSONB**
- **Large documents → object storage**
- **Vectors → Qdrant**

---

# Schema Strategy

Tailr uses a **normalized relational schema**.

Core tables:

- users
- resumes
- resume_versions
- job_descriptions
- optimization_plans
- workflows
- workflow_states
- prompts
- prompt_versions
- validation_results
- guardrail_events
- ats_results
- generated_artifacts
- audit_logs

Foreign keys enforce referential integrity.

---

# Transaction Boundaries

Critical operations execute within a single transaction.

Example:

<CodeBlock language="text" content="Create Resume Version
     ↓
Store Optimization Plan
     ↓
Store Workflow
     ↓
Store Validation Result
     ↓
Store Guardrail Events
     ↓
Store ATS Result
     ↓
Commit"/>

Either **all records are committed or none are**.

This guarantees consistency between resume versions and workflow results.

---

# Workflow State Persistence

Workflow execution is persisted explicitly.

Example states:

- Uploaded
- Parsed
- Indexed
- Planning
- Retrieval
- Rewrite
- Guardrails
- Validation
- ATS
- Rendering
- Completed
- Failed

State transitions are append-only for auditability.

---

# Guardrail Audit Storage

Every guardrail violation is persisted.

Stored fields include:

- workflow_id
- validator_name
- severity
- repaired
- violation_codes
- metadata
- created_at

This enables:

- security auditing,
- hallucination analysis,
- prompt regression testing,
- model evaluation,
- compliance reporting.

---

# Migrations

Schema changes are managed using **Alembic**.

Benefits:

- version-controlled schema,
- reproducible deployments,
- rollback support,
- CI/CD integration,
- migration history auditing.

Migration policy:

- forward-only in production,
- destructive changes require a deprecation phase,
- data migrations must be idempotent.

---

# Indexing Strategy

Indexes are created for:

- user_id
- resume_id
- workflow_id
- status
- created_at
- updated_at
- prompt_version_id

GIN indexes are used for frequently queried JSONB fields.

Indexes are added based on query profiling and observability metrics.

---

# Partitioning Strategy

The following tables are candidates for partitioning:

- audit_logs
- guardrail_events
- workflow_states
- evaluation_results

Partitioning will be introduced when table growth justifies it.

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
- Harder to enforce resume integrity

**Decision:** Rejected

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

**Decision:** Rejected

---

## Option 3 — MySQL

### Advantages

- Mature ecosystem
- Good performance

### Disadvantages

- Less capable JSON support
- Fewer advanced analytical features
- Smaller extension ecosystem

**Decision:** Rejected

---

## Option 4 — PostgreSQL

### Advantages

- ACID compliant
- JSONB support
- Excellent indexing
- Strong ecosystem
- Proven production reliability
- Rich extension support
- Excellent tooling for Python applications

### Disadvantages

- More operational complexity than SQLite
- Slightly steeper learning curve
- Requires migration discipline

**Decision:** Accepted

---

# Consequences

## Positive

- Reliable transactions
- Strong consistency
- Flexible JSONB storage
- Excellent reporting queries
- Easy schema evolution
- Mature tooling
- Better auditability
- Easier workflow analytics
- Strong guardrail event tracking

---

## Negative

- Requires migration management
- Additional operational overhead
- Larger resource footprint than SQLite
- Backup and maintenance responsibilities

---

# Risks

| Risk                      | Mitigation                             |
| ------------------------- | -------------------------------------- |
| Poor query performance    | Proper indexing and query optimization |
| Schema evolution          | Versioned Alembic migrations           |
| Large JSON fields         | Store only metadata in JSONB           |
| Database growth           | Partitioning and archival strategies   |
| Long-running transactions | Keep transaction scope small           |
| Audit table explosion     | Time-based retention policies          |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
Application Layer
│
▼
Repository Interfaces
┌─┴───────────────┐
▼                 ▼
PostgreSQL      Qdrant Cloud
(Transactional) (Vector Search)"/>

PostgreSQL and Qdrant have **strictly separate responsibilities**.

---

# Data Ownership

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Component</Table.Cell><Table.Cell>Storage</Table.Cell></Table.Row><Table.Row><Table.Cell>Users</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Canonical Resume Metadata</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Resume Versions</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Workflow State</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Workflow Transitions</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Prompt Metadata</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Validation Results</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrail Events</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>ATS Results</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Generated Artifact Metadata</Table.Cell><Table.Cell>PostgreSQL</Table.Cell></Table.Row><Table.Row><Table.Cell>Embeddings</Table.Cell><Table.Cell>Qdrant Cloud</Table.Cell></Table.Row><Table.Row><Table.Cell>Generated PDFs</Table.Cell><Table.Cell>Object Storage</Table.Cell></Table.Row><Table.Row><Table.Cell>LaTeX Source Files</Table.Cell><Table.Cell>Object Storage</Table.Cell></Table.Row></Table>

This separation prevents misuse of the relational database for vector search or large binary storage.

---

# Backup & Recovery

Backup strategy:

- Daily full backups
- WAL archiving
- Point-in-time recovery (PITR)
- Encrypted backup storage
- Quarterly restore testing

Recovery objectives:

- **RPO:** < 15 minutes
- **RTO:** < 1 hour

---

# Future Evolution

If workload characteristics change significantly, PostgreSQL may evolve into:

- read replicas,
- partitioned clusters,
- managed PostgreSQL (RDS / Cloud SQL),
- distributed PostgreSQL (Citus),
- or a dedicated analytics warehouse.

The application architecture isolates persistence behind repository interfaces, minimizing migration impact.

---

# Related ADRs

- ADR-0001 — Adopt a Canonical Resume Model
- ADR-0002 — Adopt Clean Architecture with Hexagonal Boundaries
- ADR-0003 — Use FastAPI as the Primary Backend Framework
- ADR-0005 — Use Qdrant as the Vector Database
- ADR-0006 — Adopt a Multi-Agent Workflow
- ADR-0008 — Adopt a Validation & Guardrails Engine

---

# References

- database-design.md
- data-models.md
- api-specification.md
- deployment.md
- evaluation-architecture.md

---

# Review Notes

This decision should be revisited if:

- workload characteristics become predominantly analytical,
- a distributed SQL database becomes necessary,
- application scale exceeds the operational capabilities of a single PostgreSQL instance,
- or regulatory requirements demand a different persistence architecture.

Until then, **PostgreSQL remains the authoritative transactional data store for Tailr and the system of record for all relational and workflow metadata**.

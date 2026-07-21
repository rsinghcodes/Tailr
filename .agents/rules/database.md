---
trigger: always_on
---

# Database Rules

Priority: CRITICAL

---

# Database

Primary Database

PostgreSQL 18

ORM

SQLAlchemy 2.x (Async)

Migration

Alembic

---

# General Rules

Never write raw SQL unless absolutely necessary.

Always use SQLAlchemy 2.x Core/ORM.

Always use AsyncSession.

Never persist AI-generated content whose Guardrails status is not `approved` or `repaired`.

---

# Layer Responsibility

Database access ONLY inside repositories.

Forbidden

API → Database

Service → SQLAlchemy

Domain → SQLAlchemy

Guardrails → Database

The Guardrails Engine never writes to the database directly. It returns a typed `GuardrailResult` to the calling Application Service, which is responsible for persisting both the validated content and the corresponding audit event through the appropriate repositories.

---

# Repository Rules

Repositories should:

- Read
- Write
- Update
- Delete
- Paginate
- Persist guardrail audit events (`guardrail_events`) as part of the same use case that persists the content they describe

Repositories should NOT:

- Validate business rules
- Call LLMs
- Generate prompts
- Perform orchestration
- Perform guardrail validation
- Accept AI-generated content without a `GuardrailResult` proving it was approved or repaired

A repository method that persists AI-generated resume content should accept a type that can only be constructed after a successful Guardrails check (e.g. `ApprovedResumeContent`), not a bare `str`. If the type system cannot express this, the repository must check `GuardrailResult.status` explicitly and raise rather than silently writing rejected content.

---

# Transactions

Application Services control transactions.

Repositories never commit unless explicitly required.

Preferred

async with session.begin():

Never call commit() multiple times inside one use case.

When a workflow step produces AI content, the content write and its corresponding `guardrail_events` write belong in the same transaction. Either both are committed or neither is — a resume version must never exist without its guardrail audit trail, and a guardrail audit event must never exist without knowing what it validated.

Example ordering inside one transaction:

Create Resume Version

↓

Store Optimization Plan

↓

Store Guardrail Events

↓

Store Validation Result

↓

Store ATS Result

↓

Commit

---

# Models

Separate

ORM Models

↓

Domain Models

↓

API Schemas

Never reuse one object for all layers.

`GuardrailResult` follows the same separation: an ORM model (`GuardrailEvent`) for persistence, a domain/service-level `GuardrailResult` for application logic, and an API schema for any endpoint that surfaces guardrail outcomes to the frontend. Never pass the ORM model for `guardrail_events` directly into application logic.

---

# Queries

Prefer

select()

Never use

session.query()

---

# Loading

Use

selectinload()

joinedload()

Avoid N+1 queries.

---

# Pagination

Always paginate list endpoints.

Default

20

Maximum

100

This applies to guardrail audit endpoints as well (e.g. listing `guardrail_events` for a workflow or for compliance review).

---

# Indexing

Index

Foreign Keys

Frequently searched fields

Filtering fields

Unique identifiers

For `guardrail_events` specifically, index:

workflow_id

validator_name

severity

created_at

Never index everything.

---

# UUID

Primary keys use UUIDv7 (preferred).

Never expose sequential IDs externally.

---

# Migrations

Every schema change requires Alembic migration.

Never manually edit production migrations unless necessary.

---

# Constraints

Use

NOT NULL

CHECK

UNIQUE

FOREIGN KEY

Database integrity first.

`guardrail_events` rows are append-only. No UPDATE or DELETE statements are permitted against this table outside of a documented retention/archival job. Enforce this with restricted grants, not just convention.

---

# Guardrail Audit Tables

`guardrail_events` is a first-class table, not an optional log.

Required columns:

id

workflow_id

validator_name

severity

violation_code

repaired (boolean)

metadata (JSONB)

created_at

Every guardrail execution relevant to persisted content must have a corresponding row. A resume version, optimization plan, or rendered artifact that has no associated `guardrail_events` rows is a data-integrity bug, not a missing nice-to-have.

`guardrail_events` is written by the repository layer only, on behalf of the Application Service — never by the Guardrails Engine itself (see Layer Responsibility above).

---

# Performance

Batch inserts.

Reuse sessions.

Connection pooling enabled.

Avoid SELECT \*.

Only load required columns.

Guardrail validators run independently and concurrently; their resulting audit events may be batch-inserted together in a single statement rather than one INSERT per validator.

---

# Security

Parameterized queries only.

Never concatenate SQL.

Never expose database errors.

Never expose raw resume or job description content in error messages, logs, or `guardrail_events.metadata` beyond what is strictly needed to explain a violation (e.g. violation code and section, not the full generated text).

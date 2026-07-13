# Database Rules

Priority: CRITICAL

---

# Database

Primary Database

PostgreSQL 17+

ORM

SQLAlchemy 2.x (Async)

Migration

Alembic

---

# General Rules

Never write raw SQL unless absolutely necessary.

Always use SQLAlchemy 2.x Core/ORM.

Always use AsyncSession.

---

# Layer Responsibility

Database access ONLY inside repositories.

Forbidden

API → Database

Service → SQLAlchemy

Domain → SQLAlchemy

---

# Repository Rules

Repositories should:

- Read
- Write
- Update
- Delete
- Paginate

Repositories should NOT:

- Validate business rules
- Call LLMs
- Generate prompts
- Perform orchestration

---

# Transactions

Application Services control transactions.

Repositories never commit unless explicitly required.

Preferred

async with session.begin():

Never call commit() multiple times inside one use case.

---

# Models

Separate

ORM Models

↓

Domain Models

↓

API Schemas

Never reuse one object for all layers.

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

---

# Indexing

Index

Foreign Keys

Frequently searched fields

Filtering fields

Unique identifiers

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

---

# Performance

Batch inserts.

Reuse sessions.

Connection pooling enabled.

Avoid SELECT \*.

Only load required columns.

---

# Security

Parameterized queries only.

Never concatenate SQL.

Never expose database errors.

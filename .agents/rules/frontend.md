---
trigger: always_on
---

# Frontend Rules

Priority: MEDIUM

---

# Core Principle

The frontend is a **typed, secure, accessibility-first client**.

It must never contain business logic, trust AI output blindly, or bypass backend validation.

The frontend consumes validated APIs and renders only sanitized, typed data.

---

# Framework

- Next.js (App Router)
- TypeScript (strict mode)

### Required

- `strict: true`
- `noImplicitAny: true`
- `exactOptionalPropertyTypes: true`
- `noUncheckedIndexedAccess: true`

JavaScript files are not allowed in production code.

---

# State Management

## Server State

Use **TanStack Query** for:

- API requests,
- caching,
- pagination,
- optimistic updates,
- retries,
- background refetching.

## Client State

Use **Zustand** only for UI state such as:

- theme,
- sidebar state,
- wizard progress,
- modal visibility,
- transient form drafts.

Do not store server data in Zustand.

---

# Forms & Validation

Use:

- React Hook Form
- Zod

Validation must exist on both frontend and backend.

Example:

<CodeBlock language=

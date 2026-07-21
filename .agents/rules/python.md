---
trigger: always_on
---

# Python Rules

Priority: HIGH

---

Python Version

3.13

Do not write compatibility code.

---

Formatting

Black

Ruff

PEP8

---

Typing

Every public function requires:

- parameter types
- return types

Avoid Any.

Guardrail outcomes are typed as `GuardrailResult` (status: approved / repaired / rejected, violations, warnings, metadata). Never represent a guardrail outcome as `dict`, `bool`, or `Any` — the type must make it impossible for a caller to forget to check `status`.

---

Imports

stdlib

↓

third-party

↓

internal

No wildcard imports.

---

Naming

Functions

snake_case

Classes

PascalCase

Variables

snake_case

Constants

UPPER_CASE

Guardrail validator classes are nouns describing exactly one check (`HallucinationDetector`, `PromptInjectionDetector`, `LatexSafetyValidator`) — never a generic name like `Checker` or `Validator` on its own.

---

Functions

Maximum

60 lines

Maximum

5 parameters

Prefer early returns.

A single guardrail validator function/method checks exactly one thing. If it needs more than 60 lines or starts branching on multiple unrelated concerns, split it into two validators registered in the same pipeline rather than growing one function.

---

Classes

Maximum

300 lines

Single Responsibility.

The `GuardrailsEngine` class itself is an orchestrator, not a validator — it composes individually-testable validator classes. It should not contain inline validation logic for any single check.

---

Async

Everything async.

Use

httpx.AsyncClient

AsyncSession

asyncio

Independent guardrail validators (e.g. schema validation and PII scanning, which don't depend on each other's output) run concurrently via `asyncio.gather`, not sequentially in a loop.

Never

requests

time.sleep()

Blocking IO

---

Docstrings

Google Style.

Required on:

Public classes

Public functions

Modules

A guardrail validator's docstring states what it detects and what it explicitly does not detect, so a reviewer can reason about coverage without reading the implementation.

---

Exceptions

Never raise

Exception

RuntimeError

Use typed exceptions.

A guardrail rejection raises `GuardrailRejectionError`, carrying `violation_codes` and the affected section — never a bare `ValueError` or `Exception`, and never returned as a plain `False`.

---

Logging

Never print().

Use structured logging.

Every guardrail execution logs its profile, status, violation codes, and repair actions — see Logging Rules for required fields and level mapping.

---

Configuration

Never hardcode values.

Read from Settings.

Guardrail profiles, enabled validators, and thresholds are read from Settings, never hardcoded as literals or inline conditionals inside a validator.

---

Files

One responsibility per module.

Avoid giant files.

Each guardrail validator lives in its own module inside `guardrails/`. The pipeline composition (which validators run, in what order, per profile) lives in one place, not scattered across validator modules.

---

Performance

Avoid unnecessary allocations.

Reuse clients.

Prefer generators.

Batch operations.

Run independent guardrail validators concurrently rather than sequentially to keep guardrail overhead small relative to the LLM call it follows.

---

Security

Never log secrets.

Never deserialize untrusted input.

Always validate.

Raw LLM output is untrusted input. It is JSON-parsed and schema-validated by the Guardrails Engine before it is deserialized into any domain model, and it is never `eval()`'d, `pickle.loads()`'d, or otherwise deserialized through an unsafe mechanism regardless of source.

---

Code Generation

Prefer readability.

Prefer maintainability.

Avoid clever solutions.

Never write an ad hoc validation shortcut inline to handle "just this one case" of unsafe AI output. Extend the Guardrails Engine with a proper validator instead — a clever one-off check that bypasses Guardrails is exactly the kind of clever solution this rule exists to prevent.

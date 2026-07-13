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

---

Functions

Maximum

60 lines

Maximum

5 parameters

Prefer early returns.

---

Classes

Maximum

300 lines

Single Responsibility.

---

Async

Everything async.

Use

httpx.AsyncClient

AsyncSession

asyncio

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

---

Exceptions

Never raise

Exception

RuntimeError

Use typed exceptions.

---

Logging

Never print().

Use structured logging.

---

Configuration

Never hardcode values.

Read from Settings.

---

Files

One responsibility per module.

Avoid giant files.

---

Performance

Avoid unnecessary allocations.

Reuse clients.

Prefer generators.

Batch operations.

---

Security

Never log secrets.

Never deserialize untrusted input.

Always validate.

---

Code Generation

Prefer readability.

Prefer maintainability.

Avoid clever solutions.

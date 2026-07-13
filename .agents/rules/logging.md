# Logging Rules

Priority: HIGH

---

Use structured logging.

Never print().

---

Required Fields

request_id

correlation_id

module

operation

duration_ms

status

---

Levels

DEBUG

Development only

INFO

Business events

WARNING

Recoverable issues

ERROR

Failures

CRITICAL

Application cannot continue

---

Never Log

Passwords

Tokens

Secrets

API Keys

Resume content

Personal data

---

Always Log

Startup

Shutdown

Database failures

Provider failures

Workflow completion

Background jobs

---

Use JSON logs.

Every request receives a Request ID.

Correlation IDs propagate across workflows.

Support OpenTelemetry trace IDs.

---
trigger: always_on
---

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
For any log emitted by or about the Guardrails Engine, additionally required:
workflow_id
guardrail_profile
guardrail_status (approved / repaired / rejected)
violation_codes (empty list if none)
repair_applied (boolean)

---

Levels
DEBUG
Development only
INFO
Business events
Guardrails approved (no violations, no repair)
WARNING
Recoverable issues
Guardrails repaired (issue found and automatically fixed — this is recoverable but must not be invisible; log it as a warning, not INFO, so repair frequency is monitorable)
ERROR
Failures
Guardrails rejected (workflow step failed as a direct result — this is an application-level failure, not a silent business outcome)
Guardrail validator itself throwing (e.g. a detector crashing) — distinct from a rejection, and must fail closed per the Guardrails Architecture, never fail open
CRITICAL
Application cannot continue
Guardrails Engine unavailable or misconfigured such that no validation can run — this must halt AI-output-consuming workflows, not silently bypass Guardrails and continue

---

Never Log
Passwords
Tokens
Secrets
API Keys
Resume content
Personal data
Job description content
Full AI-generated output — even when logging a Guardrails rejection, log the violation codes and affected section, never the full generated text that triggered them

---

Always Log
Startup
Shutdown
Database failures
Provider failures
Workflow completion
Background jobs
Every Guardrails Engine execution, regardless of outcome — a guardrail check that ran but was never logged is functionally unauditable and violates the Guardrails Architecture's full-auditability principle
Every guardrail repair action, with the specific repair applied (e.g. "stripped markdown fence", "escaped unsafe character")
Every guardrail rejection, with violation codes and the affected resume section

---

Use JSON logs.
Every request receives a Request ID.
Correlation IDs propagate across workflows, including through every Guardrails Engine invocation within that workflow.
Support OpenTelemetry trace IDs.
Guardrails logs must carry the same trace ID as the workflow step that produced the content being validated, so a rejection can be traced back to the exact prompt/agent/provider call that caused it.

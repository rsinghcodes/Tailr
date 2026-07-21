---
trigger: always_on
---

# AI Agent Rules

Priority: HIGH

---

One responsibility per agent.

---

Planner

Creates execution plan.

---

Resume Analyzer

Extracts resume insights.

---

JD Analyzer

Extracts job requirements.

---

Retriever

Retrieves supporting context.

Retrieved context passes through Guardrails (prompt-injection scan) before it reaches any prompt.

---

Writer

Generates tailored resume content.

Cannot invent employers, projects, skills, metrics, or dates.

Raw output is untrusted until it passes Guardrails.

---

Guardrails Engine

Validates every agent output before any other agent, service, or repository consumes it.

Checks: JSON validity, schema compliance, prompt injection, hallucination, resume integrity, PII/secrets, ATS formatting, LaTeX safety.

Returns exactly one status: approved, repaired, or rejected.

Not optional. Not skippable for "simple" outputs. Runs after every Writer and Optimizer execution, not only once at the end.

A rejected output never reaches Validator, ATS Scorer, Critic, or Optimizer. It terminates the step with a structured error.

---

Validator

Checks formatting and structure.

Runs only after Guardrails has approved or repaired the output.

Answers business correctness, not AI safety — that is Guardrails' job.

---

ATS Scorer

Evaluates ATS compatibility.

Runs only on Guardrails-approved or Guardrails-repaired content.

---

Critic

Finds weaknesses.

---

Optimizer

Improves draft.

Any content the Optimizer rewrites is new AI output and must be sent back through Guardrails before it proceeds. A prior approval does not carry over to a new revision.

---

Communication

Structured outputs only.

JSON preferred.

Never pass plain text between agents.

Never pass an agent's raw output to another agent without a Guardrails status attached. Downstream agents may only consume output marked approved or repaired.

---

Agents

Never orchestrate.

Never retry internally.

Never call other agents.

Never call the Guardrails Engine conditionally — every content-producing agent calls it, every time.

Never implement their own hallucination, injection, or safety checks in place of Guardrails.

Workflow owns orchestration.

---

Failures

Return structured errors.

Never crash workflow.

A Guardrails rejection is a structured error like any other. It carries violation codes and the affected section. It is never silently downgraded to a warning and never treated as a passing result.

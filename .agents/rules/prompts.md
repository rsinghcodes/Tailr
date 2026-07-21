---
trigger: always_on
---

# Prompt Engineering Rules

Prompts live only in

backend/prompts/

Never inline prompts.

---

Every prompt

Versioned

Documented

Deterministic

Assigned a Guardrail Profile (`rewrite_strict` / `analysis_standard` / `validation_paranoid`)

A prompt version cannot be promoted to production without a guardrail profile declared in its metadata. "No profile assigned" is not a valid default — it must be explicitly chosen.

---

Use

System Prompt

↓

Developer Prompt

↓

User Prompt

Retrieved context and job description text are never concatenated into the System or Developer Prompt as if they were instructions. They are passed as clearly delimited data within the User Prompt, and are scanned by Guardrails for prompt-injection patterns before assembly — retrieval is not a trusted channel just because it came from the knowledge base.

---

Prefer

Structured Outputs

JSON Schema

Pydantic validation

Structured output schema validation is the first stage of the Guardrails pipeline (JSON Parse → Schema Validation), not a separate concern from Guardrails. A prompt's declared output schema and the schema Guardrails validates against must be the same schema — never two schemas maintained separately that can drift.

---

Never trust LLM output.

Always validate.

"Validate" means two distinct, sequential stages, in this order:

1. Guardrails Engine — JSON validity, schema compliance, prompt injection, hallucination (against the Canonical Resume Model), resume integrity, PII/secrets, ATS formatting, LaTeX safety.
2. Business Validators — business-rule correctness.

A prompt is not considered production-ready until its output has been exercised against both stages, including adversarial inputs (known injection patterns, inputs designed to elicit fabricated skills/employers/metrics).

---

Keep prompts

Focused

Short

Composable

Reusable

A prompt that tries to both generate content and self-police its own safety ("do not hallucinate", "only use provided facts") is not a substitute for Guardrails. Instructional safety hints in a prompt are a reasonable first line of defense to reduce Guardrails repair/rejection rate, but they are never a replacement for the deterministic Guardrails check that follows.

---

Track

Prompt version

Model

Temperature

Max Tokens

Latency

Token usage

Guardrail pass rate (approved without repair)

Guardrail repair rate

Guardrail rejection rate

Hallucination detection rate

Prompt injection detection count

A prompt version with a rising rejection or repair rate is a regression signal — treat it the same as a latency or cost regression and route it through the Evaluation Pipeline (ADR-0010) before it stays in production.

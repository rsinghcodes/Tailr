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

---

Writer

Generates tailored resume.

---

Validator

Checks formatting and structure.

---

ATS Scorer

Evaluates ATS compatibility.

---

Critic

Finds weaknesses.

---

Optimizer

Improves draft.

---

Communication

Structured outputs only.

JSON preferred.

Never pass plain text between agents.

---

Agents

Never orchestrate.

Never retry internally.

Never call other agents.

Workflow owns orchestration.

---

Failures

Return structured errors.

Never crash workflow.

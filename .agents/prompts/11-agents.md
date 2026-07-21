# AI Agents — Production Implementation Prompt

## Objective

Implement the complete production-ready **AI Agent system** for Tailr.

This module contains all specialized AI agents that perform reasoning tasks within the resume optimization workflow.

The AI Agent system is responsible for:

- JD Analyzer agent,
- Planning agent,
- Rewrite agent,
- ATS Advisor agent,
- Critic agent,
- Optimizer agent,
- agent base interface,
- provider abstraction,
- structured output enforcement,
- prompt template integration,
- guardrails integration,
- retry and timeout handling,
- and agent telemetry.

Each agent has **exactly one responsibility** and communicates through **typed structured interfaces**.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/ai-agents.md
- rules/prompts.md
- rules/security.md
- rules/testing.md
- rules/logging.md
- ADR-0002 — Clean Architecture
- ADR-0006 — Adopt Multi-Agent Architecture
- ADR-0008 — Model Provider Abstraction
- ADR-0009 — Prompt Versioning
- ADR-0011 — Validation & Guardrails Engine
- 02-Agent-Architecture.md
- 08-LLM-Prompt-Design.md
- 09-Guardrails-Architecture.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Architecture Constraints

## Agent Rules

- one responsibility per agent
- structured outputs only (JSON/Pydantic)
- never pass plain text between agents
- agents never orchestrate other agents
- agents never retry internally
- agents never call the Guardrails Engine conditionally — every content-producing agent calls it, every time
- agents never implement their own ad-hoc validation logic as a substitute for Guardrails
- downstream agents may only consume output marked `approved` or `repaired`

## Orchestration

Agents are orchestrated by **LangGraph** (ADR-0007). Agents never control workflow state, retries, or scheduling — those responsibilities belong to the LangGraph workflow engine.

## Retrieval

Knowledge retrieval uses **LlamaIndex** (ADR-0005). Agents receive retrieved context from LlamaIndex via the workflow; they do not call LlamaIndex directly.

## Communication

All agents communicate through typed Pydantic models:

```text
PlannerOutput → RewriteInput → RewriteOutput → ValidationInput
```

## Provider Abstraction

Application never knows which LLM provider is used.

```text
Application → LLMProvider → OllamaProvider / OpenAIProvider / HFProvider
```

No provider is trusted more than another. Every provider's output passes through the same Guardrails Engine.

---

# Agent Definitions

---

## JD Analyzer Agent

### Purpose

Convert an unstructured Job Description into structured requirements.

### Input

```python
JDAnalysisInput(
    raw_text: str,
    metadata: dict,
)
```

### Output

```python
JDAnalysisOutput(
    title: str,
    required_skills: list[str],
    preferred_skills: list[str],
    responsibilities: list[str],
    keywords: list[str],
    soft_skills: list[str],
    experience_level: str,
    certifications: list[str],
)
```

### Guardrail Profile

`analysis_standard` — schema validation, JSON validation, prompt injection detection.

### Constraints

- must never rewrite resumes
- must never infer user experience
- must produce deterministic JSON

---

## Planning Agent

### Purpose

Determine how the resume should be optimized. Creates an optimization strategy. Never edits text.

### Input

```python
PlanningInput(
    resume: Resume,
    job_requirements: JobRequirements,
    retrieved_chunks: list[RetrievalResult],
)
```

### Output

```python
PlanningOutput(
    summary_changes: list[SectionChange],
    experience_changes: list[SectionChange],
    project_changes: list[SectionChange],
    skill_changes: list[SectionChange],
    reasoning: str,
)
```

### Guardrail Profile

`analysis_standard`

### Constraints

- no rewriting text
- no inventing skills
- no fabricating projects
- no modifying dates
- must cite retrieved evidence

---

## Rewrite Agent

### Purpose

Rewrite resume content according to the approved plan.

### Input

```python
RewriteInput(
    resume: Resume,
    rewrite_plan: PlanningOutput,
    retrieved_context: list[RetrievalResult],
)
```

### Output

```python
RewriteOutput(
    updated_resume: Resume,
    modified_sections: list[str],
    confidence: float,
    citations: list[Citation],
)
```

### Guardrail Profile

`rewrite_strict` — hallucination detection, integrity validation, ATS validation, LaTeX safety.

### Constraints

- cannot invent employers, projects, metrics, dates, or technologies
- rewrite only, never reason about whether a section should change (planning has already happened)
- preserve all immutable facts

---

## ATS Advisor Agent

### Purpose

Explain optimization quality and generate ATS compatibility analysis.

### Input

```python
ATSAnalysisInput(
    original_resume: Resume,
    optimized_resume: Resume,
    job_requirements: JobRequirements,
)
```

### Output

```python
ATSAnalysisOutput(
    overall_score: int,
    keyword_coverage: float,
    missing_keywords: list[str],
    strengths: list[str],
    weaknesses: list[str],
    recommendations: list[str],
)
```

### Guardrail Profile

`analysis_standard`

### Constraints

- cannot modify resumes
- analysis only

---

## Critic Agent

### Purpose

Find weaknesses in the optimized resume and suggest improvements.

### Input

```python
CriticInput(
    optimized_resume: Resume,
    job_requirements: JobRequirements,
    ats_report: ATSAnalysisOutput,
)
```

### Output

```python
CriticOutput(
    weaknesses: list[Weakness],
    improvement_suggestions: list[Suggestion],
    severity_assessment: str,
)
```

### Guardrail Profile

`analysis_standard`

---

## Optimizer Agent

### Purpose

Improve the draft based on Critic feedback.

### Input

```python
OptimizerInput(
    resume: Resume,
    critic_feedback: CriticOutput,
    rewrite_plan: PlanningOutput,
    retrieved_context: list[RetrievalResult],
)
```

### Output

```python
OptimizerOutput(
    updated_resume: Resume,
    changes_applied: list[str],
    confidence: float,
)
```

### Guardrail Profile

`rewrite_strict` — any content the Optimizer rewrites is new AI output and must be sent back through Guardrails. A prior approval does not carry over.

---

# Agent Base Interface

```python
class BaseAgent(Protocol):
    agent_name: str
    guardrail_profile: str

    async def execute(self, input: AgentInput) -> AgentOutput: ...
```

### Requirements

- every agent implements `BaseAgent`
- every agent declares its guardrail profile
- every agent produces structured output
- every agent logs execution telemetry

---

# Provider Abstraction

```python
class LLMProvider(Protocol):
    async def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> LLMResponse: ...
    async def generate_structured(self, prompt: str, model: str, output_schema: type[BaseModel]) -> BaseModel: ...
    async def health_check(self) -> HealthStatus: ...
```

### Implementations

- `OllamaProvider`
- `OpenAIProvider` (future-ready)
- `AnthropicProvider` (future-ready)
- `HuggingFaceProvider` (future-ready)

### Model Selection

Different reasoning tasks may use different models:

| Task          | Default Model |
| ------------- | ------------- |
| JD Extraction | Qwen3 8B     |
| Planning      | Qwen3 14B    |
| Rewriting     | Llama 3.1    |
| ATS Analysis  | Gemma 3      |

Model selection is configurable without code changes.

---

# Prompt Integration

- all prompts live in `backend/prompts/`
- never inline prompts inside agent code
- every prompt declares a guardrail profile in its metadata
- every prompt has a versioned identifier
- prompt and guardrail schema must be the same schema (never maintained separately)

---

# Error Handling

- every agent failure returns a structured error
- agents never crash the workflow
- a guardrail rejection is a structured error carrying violation codes
- provider failures raise `ProviderError`
- timeout failures raise `AgentTimeoutError`

---

# Retry and Timeout

- configurable retry attempts per agent
- exponential backoff
- configurable timeout per agent
- timeout failures are logged and reported

---

# Telemetry

Every agent emits:

- agent_name
- prompt_version
- model_name
- token_count (input + output)
- latency_ms
- retry_count
- success/failure status
- guardrail profile used
- guardrail outcome

---

# Required File Structure

```text
agents/
├── __init__.py
├── base.py
├── jd_analyzer.py
├── planner.py
├── rewriter.py
├── ats_advisor.py
├── critic.py
├── optimizer.py
├── contracts/
│   ├── __init__.py
│   ├── jd_analysis.py
│   ├── planning.py
│   ├── rewriting.py
│   ├── ats_analysis.py
│   ├── critic.py
│   └── optimizer.py
├── exceptions.py
└── telemetry.py

providers/
├── __init__.py
├── base.py
├── ollama.py
├── openai.py
└── models.py
```

---

# Testing Requirements

Generate tests for:

- each agent (valid input, invalid input, provider failure),
- structured output validation,
- guardrail approved path,
- guardrail repaired path,
- guardrail rejected path,
- adversarial tests (prompt injection attempts, hallucination scenarios),
- provider abstraction (mock providers),
- retry behavior,
- timeout behavior,
- telemetry emission,
- contract validation (input/output schemas),
- and model selection configuration.

Use: pytest, pytest-asyncio, mock LLM providers.

Target coverage: **90%+**.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- have one responsibility per agent,
- be async-first,
- avoid global mutable state,
- and be production deployable.

---

# Output Requirements

Return:

1. complete source files,
2. test files,
3. agent architecture diagram,
4. agent communication flow,
5. provider abstraction explanation,
6. guardrail integration per agent,
7. retry/timeout strategy,
8. telemetry design,
9. prompt integration explanation,
10. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready AI Agent system** that provides:

- specialized single-responsibility agents,
- provider abstraction,
- structured input/output contracts,
- guardrails integration at every generation step,
- retry and timeout handling,
- comprehensive telemetry,
- and adversarial testing

for the Tailr platform.

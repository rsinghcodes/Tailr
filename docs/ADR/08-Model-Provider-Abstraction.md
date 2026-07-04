# ADR-0008: Adopt a Model Provider Abstraction Layer with Ollama as the Default Inference Provider

**Status:** Accepted

**Date:** 2026-07-04

**Authors:** Tailr Engineering

---

# Context

Tailr relies heavily on Large Language Models (LLMs) for nearly every AI capability, including:

- Resume analysis
- Job description understanding
- Resume rewriting
- Planning
- Validation
- ATS scoring
- Retrieval-augmented generation (RAG)

Using a single model provider directly throughout the codebase would tightly couple business logic to one vendor.

Additionally, different tasks benefit from different models.

For example:

- Small models for keyword extraction
- Medium models for planning
- Larger models for rewriting
- Embedding models for retrieval

The platform therefore requires a provider-independent inference layer.

---

# Decision

Tailr adopts a **Model Provider Abstraction Layer (MPAL)**.

All AI requests pass through a unified interface.

The initial implementation uses **Ollama** as the default inference provider.

Future providers can be added without changing business logic.

---

# Decision Drivers

The inference layer must:

- Support multiple LLM providers
- Enable local-first development
- Reduce vendor lock-in
- Support model routing
- Enable cost optimization
- Allow future cloud deployment
- Support structured outputs

---

# Architecture

```
                AI Agent
                    │
                    ▼
        Model Provider Interface
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
 Ollama        OpenAI Adapter   Anthropic Adapter
     │
     ▼
Selected Model
```

Agents never call providers directly.

---

# Provider Interface

Example:

```python
class LLMProvider:

    async def generate(
        self,
        prompt: Prompt,
        config: GenerationConfig
    ) -> AIResponse:
        ...
```

Every provider implements the same interface.

---

# Initial Provider

Default implementation:

```
Ollama
```

Supported local models include:

- Qwen 3
- Gemma 3
- Llama 3.x
- DeepSeek-R1
- Mistral
- Phi-4

Models remain configurable.

---

# Model Selection

Different agents may use different models.

Example:

| Agent           | Model                          |
| --------------- | ------------------------------ |
| JD Analyzer     | Qwen 3 4B                      |
| Resume Analyzer | Qwen 3 8B                      |
| Planner         | Qwen 3 14B                     |
| Rewriter        | Llama 3.3 70B (cloud optional) |
| Validator       | Gemma 3                        |

Model routing is configuration-driven rather than hardcoded.

---

# Structured Output

Every AI response should conform to a schema.

Example:

```json
{
  "summary": "...",
  "missing_keywords": [],
  "recommendations": []
}
```

Schema validation occurs after generation.

---

# Prompt Isolation

The provider layer receives:

- system prompt
- user prompt
- response schema
- model configuration
- generation parameters

Prompt construction remains outside provider implementations.

---

# Streaming Support

The provider interface supports:

- synchronous generation
- streaming responses
- incremental token delivery

Streaming enables future real-time UI updates.

---

# Provider Configuration

Each model defines:

- context window
- temperature
- top_p
- max_tokens
- timeout
- retry policy

Configuration is externalized.

---

# Fallback Strategy

If a provider fails:

```
Primary Model

↓

Retry

↓

Fallback Model

↓

Workflow Failure
```

Fallback policies are configurable.

---

# Caching

The provider layer supports:

- prompt cache
- response cache
- embedding cache

Repeated requests avoid unnecessary inference.

---

# Alternatives Considered

## Option 1 — Direct OpenAI Integration

### Advantages

- Simple implementation
- High-quality models

### Disadvantages

- Vendor lock-in
- Ongoing API costs
- Internet dependency

Decision: Rejected

---

## Option 2 — Direct Ollama Integration

### Advantages

- Local execution
- No API costs

### Disadvantages

- Tight coupling
- Difficult provider replacement

Decision: Rejected

---

## Option 3 — Model Provider Abstraction Layer

### Advantages

- Provider independence
- Easier testing
- Configurable routing
- Future-proof architecture
- Supports local and cloud inference

### Disadvantages

- Additional abstraction
- Slight implementation complexity

Decision: Accepted

---

# Consequences

## Positive

- No vendor lock-in
- Easy provider replacement
- Supports multiple models
- Local-first development
- Better testability
- Cleaner architecture

---

## Negative

- More infrastructure code
- Provider compatibility testing
- Configuration management

---

# Risks

| Risk                       | Mitigation                |
| -------------------------- | ------------------------- |
| Provider API changes       | Adapter pattern           |
| Model quality differences  | Evaluation framework      |
| Local resource limitations | Optional cloud providers  |
| Slow inference             | Model routing and caching |

---

# Architecture Integration

```
FastAPI

↓

Workflow Engine

↓

Agents

↓

LLM Provider Interface

↓

Ollama / OpenAI / Anthropic

↓

AI Response
```

The provider layer isolates the rest of the application from model-specific APIs.

---

# Related ADRs

- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture
- ADR-0005 — LlamaIndex as the AI Data Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine

---

# References

- Agent-Architecture.md
- Workflow-Design.md
- RAG-Architecture.md
- Deployment.md
- Observability.md

---

# Review Notes

This decision should be revisited if:

- inference requirements change significantly,
- new provider standards emerge,
- or local-first execution no longer meets product goals.

Until then, the Model Provider Abstraction Layer with Ollama as the default implementation remains the standard approach for AI inference within Tailr.

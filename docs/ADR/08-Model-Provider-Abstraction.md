# ADR-0008: Adopt an LLM Router and Provider Abstraction Layer with Ollama as the Default Inference Provider

**Status:** Accepted

**Date:** 2026-07-20

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
- Retrieval-Augmented Generation (RAG)
- Guardrail repair
- Evaluation and benchmarking

Using a single provider directly throughout the codebase would tightly couple business logic to one vendor and make model replacement expensive.

Different tasks also benefit from different model sizes and capabilities:

- small models for keyword extraction,
- medium models for planning,
- larger models for rewriting,
- specialized models for validation,
- embedding models for retrieval.

The platform therefore requires a **provider-independent inference layer with intelligent model routing**.

---

# Decision

Tailr adopts an **LLM Router and Provider Abstraction Layer (LLM-RPAL)**.

All AI requests pass through a unified interface.

The initial implementation uses **Ollama** as the default inference provider for local-first development.

Future providers (OpenAI, Anthropic, Gemini, and others) can be added without changing business logic or agent implementations.

---

# Decision Drivers

The inference layer must:

- support multiple LLM providers,
- enable local-first development,
- reduce vendor lock-in,
- support intelligent model routing,
- enable cost optimization,
- support cloud and hybrid deployments,
- enforce structured outputs,
- support streaming responses,
- provide observability and token accounting,
- isolate provider-specific APIs.

---

# Architecture

<CodeBlock language="text" content="                AI Agent
                 │
                 ▼
           LLM Router
                 │
       Provider Interface
                 │
  ┌──────────────┼──────────────┐
  ▼              ▼              ▼
Ollama         OpenAI Adapter   Anthropic Adapter
  │
  ▼
Selected Model"/>

Agents never call providers directly.

The **LLM Router** selects the provider and model based on task requirements and routing policy.

---

# Provider Interface

<CodeBlock language="python" content="class LLMProvider(Protocol):
async def generate(
self,
request: GenerationRequest
) -> GenerationResponse:
...

```
async def stream(
    self,
    request: GenerationRequest
) -> AsyncIterator[TokenChunk]:
    ..."/>
```

All providers implement the same interface, enabling provider substitution without changing application code.

---

# LLM Router

The router is responsible for:

- selecting the provider,
- selecting the model,
- applying routing policies,
- enforcing timeouts,
- applying retry policies,
- recording telemetry,
- triggering fallback providers.

Example:

<CodeBlock language="python" content="response = await llm_router.generate(
task="rewrite",
request=request
)"/>

---

# Default Provider

The default implementation is:

<CodeBlock language="text" content="Ollama"/>

Supported local models include:

- Qwen 3
- Gemma 3
- Llama 3.x
- DeepSeek-R1
- Mistral
- Phi-4

Model names remain configuration-driven and are not hardcoded in business logic.

---

# Model Capability Registry

Each model declares its capabilities.

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Capability</Table.Cell><Table.Cell>Example</Table.Cell></Table.Row><Table.Row><Table.Cell>chat</Table.Cell><Table.Cell>Qwen3-8B</Table.Cell></Table.Row><Table.Row><Table.Cell>structured_output</Table.Cell><Table.Cell>Gemma3</Table.Cell></Table.Row><Table.Row><Table.Cell>long_context</Table.Cell><Table.Cell>Llama3-70B</Table.Cell></Table.Row><Table.Row><Table.Cell>streaming</Table.Cell><Table.Cell>Qwen3-14B</Table.Cell></Table.Row><Table.Row><Table.Cell>tool_calling</Table.Cell><Table.Cell>Future providers</Table.Cell></Table.Row></Table>

The router uses this registry during model selection.

---

# Task-Based Model Routing

Different agents may use different models.

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Agent</Table.Cell><Table.Cell>Default Model</Table.Cell></Table.Row><Table.Row><Table.Cell>JD Analyzer</Table.Cell><Table.Cell>Qwen3-4B</Table.Cell></Table.Row><Table.Row><Table.Cell>Resume Analyzer</Table.Cell><Table.Cell>Qwen3-8B</Table.Cell></Table.Row><Table.Row><Table.Cell>Planning Agent</Table.Cell><Table.Cell>Qwen3-14B</Table.Cell></Table.Row><Table.Row><Table.Cell>Rewrite Agent</Table.Cell><Table.Cell>Qwen3-14B / Cloud fallback</Table.Cell></Table.Row><Table.Row><Table.Cell>Validation Agent</Table.Cell><Table.Cell>Gemma3</Table.Cell></Table.Row><Table.Row><Table.Cell>Guardrail Repair</Table.Cell><Table.Cell>Gemma3</Table.Cell></Table.Row></Table>

Routing is configuration-driven rather than hardcoded.

---

# Structured Output Enforcement

Every AI response must conform to a schema.

Example:

<CodeBlock language="json" content="{
"summary": "...",
"missing_keywords": [],
"recommendations": []
}"/>

The provider layer:

- requests structured output,
- parses the response,
- validates against the schema,
- returns typed objects,
- raises structured errors on validation failure.

---

# Prompt Isolation

The provider layer receives:

- system prompt,
- user prompt,
- response schema,
- model configuration,
- generation parameters,
- token budget,
- timeout,
- trace context.

Prompt construction remains outside provider implementations.

This keeps providers generic and reusable.

---

# Streaming Support

The interface supports:

- standard generation,
- streaming generation,
- incremental token delivery,
- cancellation propagation.

Streaming enables real-time UI progress updates and future conversational features.

---

# Embedding Provider Separation

Embedding generation is handled by a separate interface.

<CodeBlock language="python" content="class EmbeddingProvider(Protocol):
 async def embed(self, texts: list[str]) -> list[list[float]]:
     ..."/>

This prevents chat-model assumptions from leaking into retrieval infrastructure.

---

# Fallback Strategy

If a provider fails:

<CodeBlock language="text" content="Primary Model
   ↓
Retry (same provider)
   ↓
Fallback Model
   ↓
Fallback Provider
   ↓
Workflow Failure"/>

Example policy:

<Table columnSizing="equal" rowDivider={{"size":1,"color":"default"}}><Table.Row header><Table.Cell>Stage</Table.Cell><Table.Cell>Fallback</Table.Cell></Table.Row><Table.Row><Table.Cell>Qwen3-14B</Table.Cell><Table.Cell>Qwen3-8B</Table.Cell></Table.Row><Table.Row><Table.Cell>Ollama unavailable</Table.Cell><Table.Cell>OpenAI GPT-4o-mini</Table.Cell></Table.Row><Table.Row><Table.Cell>Structured output failure</Table.Cell><Table.Cell>Gemma3 repair pass</Table.Cell></Table.Row></Table>

Fallback policies are centrally managed.

---

# Caching

The abstraction layer supports:

- prompt cache,
- response cache,
- embedding cache,
- semantic cache (future).

Cache keys include:

- model,
- prompt hash,
- schema version,
- generation parameters.

This reduces latency and inference cost.

---

# Guardrails Integration

The provider layer does **not** make trust decisions.

All responses are forwarded to the **Guardrails Engine** for:

- schema validation,
- prompt injection detection,
- hallucination detection,
- PII detection,
- policy enforcement,
- output repair.

Guardrails remain independent of provider implementations.

---

# Observability

Every request records:

- workflow ID,
- agent name,
- provider,
- model,
- prompt version,
- input tokens,
- output tokens,
- latency,
- retry count,
- fallback usage,
- estimated cost,
- streaming duration.

Telemetry is exported through **OpenTelemetry**.

---

# Configuration

Provider configuration is externalized.

<CodeBlock language="yaml" content="llm:
default_provider: ollama

providers:
ollama:
base_url: http://localhost:11434
timeout: 120

```
openai:
  api_key: ${OPENAI_API_KEY}
  timeout: 60
```

routing:
rewrite: qwen3:14b
planning: qwen3:14b
validation: gemma3"/>

No provider credentials are stored in code.

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
- Harder offline development

**Decision:** Rejected

---

## Option 2 — Direct Ollama Integration

### Advantages

- Local execution
- No API costs
- Full data privacy

### Disadvantages

- Tight coupling
- Difficult provider replacement
- No routing abstraction

**Decision:** Rejected

---

## Option 3 — Provider Abstraction without Router

### Advantages

- Provider independence
- Simpler implementation

### Disadvantages

- No intelligent routing
- Harder cost optimization
- Manual model selection everywhere

**Decision:** Rejected

---

## Option 4 — LLM Router + Provider Abstraction Layer

### Advantages

- Provider independence
- Intelligent routing
- Easier testing
- Configurable policies
- Supports local and cloud inference
- Future-proof architecture
- Centralized observability

### Disadvantages

- Additional abstraction
- More infrastructure code
- Provider compatibility testing

**Decision:** Accepted

---

# Consequences

## Positive

- No vendor lock-in
- Easy provider replacement
- Intelligent model selection
- Local-first development
- Better testability
- Centralized telemetry
- Cleaner architecture
- Easier future cloud migration

---

## Negative

- More infrastructure code
- Additional configuration management
- Need to maintain provider adapters
- Requires compatibility testing across providers

---

# Risks

| Risk                              | Mitigation                    |
| --------------------------------- | ----------------------------- |
| Provider API changes              | Adapter pattern               |
| Model quality differences         | Evaluation framework          |
| Local resource limitations        | Optional cloud providers      |
| Slow inference                    | Routing and caching           |
| Structured output incompatibility | Guardrails repair stage       |
| Cost spikes                       | Budget-aware routing policies |

---

# Architecture Integration

<CodeBlock language="text" content="FastAPI
│
▼
Workflow Engine
│
▼
AI Agents
│
▼
LLM Router
│
▼
Provider Interface
├── Ollama
├── OpenAI
├── Anthropic
└── Gemini
     │
     ▼
Guardrails
     │
     ▼
Typed AI Response"/>

The router isolates the rest of the application from provider-specific APIs and routing complexity.

---

# Future Enhancements

Planned enhancements include:

- budget-aware routing,
- latency-aware routing,
- automatic model benchmarking,
- dynamic provider health checks,
- multi-model consensus,
- speculative decoding,
- distributed inference,
- GPU-aware routing,
- prompt optimization feedback loops.

The current abstraction is designed so these capabilities can be added incrementally.

---

# Related ADRs

- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture with Hexagonal Boundaries
- ADR-0005 — LlamaIndex as the AI Data and Workflow Framework
- ADR-0006 — Multi-Agent Architecture
- ADR-0007 — Event-Driven Workflow Engine

---

# References

- agent-architecture.md
- workflow-design.md
- rag-architecture.md
- deployment.md
- observability.md
- evaluation-architecture.md

---

# Review Notes

This decision should be revisited if:

- inference requirements change significantly,
- a new provider standard emerges,
- local-first execution no longer meets product goals,
- or operational complexity outweighs the benefits of provider abstraction.

Until then, the **LLM Router and Provider Abstraction Layer with Ollama as the default implementation remains the standard inference architecture for Tailr**, providing provider independence, intelligent model routing, structured outputs, and centralized observability.

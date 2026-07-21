---
trigger: always_on
---

# FastAPI Rules

## Priority: HIGH

API Layer Responsibilities
Routes only.
No business logic.
No guardrail logic. Routers never call validators, never inspect a `GuardrailResult`, and never decide what to do with a rejection — they only translate whatever typed exception the Application layer raises into an HTTP response.

---

Every endpoint requires
Request model
Response model
Dependency Injection
Error handling
Logging
For any endpoint whose response can contain AI-generated content: a documented error response for the Guardrails-rejected case.

---

Routers
One router per domain.
Example
resume.py
job.py
health.py
admin.py
guardrails.py (audit/read-only endpoints only — e.g. list guardrail events for a workflow; never an endpoint that runs guardrail checks directly from a router)

---

Dependencies
Always use Depends().
Never instantiate services.
Never instantiate a `GuardrailsEngine` or an individual validator inside a router. If a router needs guardrail outcomes (e.g. an audit endpoint), inject the Application Service that already coordinates with Guardrails — never call the Guardrails port directly from `api/`.

---

Responses
Always use response models.
Never return ORM objects.
Never return AI-generated content in a response model unless the Application layer has already confirmed its `GuardrailResult.status` was `approved` or `repaired`. The response model has no field for "unvalidated content" — if the service hands the router something that hasn't been through Guardrails, that is an Application-layer bug, not something the router should work around.

---

Validation
Pydantic v2.
Strict validation.

---

Errors
Return standardized API responses.
Never expose tracebacks.
A `GuardrailRejectionError` raised by the Application layer is caught by a dedicated exception handler and converted into a standardized error response containing the violation codes and affected section — never a generic 500, and never silently converted into a 200 with degraded content.

---

Status Codes
Use correct HTTP status codes.
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
422 Unprocessable Entity — Guardrails Rejected (same code as validation errors; the response body's `error` field distinguishes a business validation failure from a Guardrails rejection via a distinct error code, e.g. `guardrail_rejected`)
500 Internal Server Error
A Guardrails rejection is never mapped to 500. It is a well-formed, expected outcome of AI generation, not a server fault.

---

Versioning
All endpoints under
/api/v1

---

Middleware
Request ID
Correlation ID
Logging
Metrics
Security Headers
Compression
CORS
Guardrails is never implemented as middleware. It runs inside the Application layer, scoped to the specific use case that produced the AI output, with access to the Canonical Resume Model and the correct guardrail profile for that task — a generic request/response middleware has neither.

---

OpenAPI
Every endpoint documented.
Every schema documented.
Any endpoint that can return a Guardrails-rejected error documents that error shape in its OpenAPI response schemas, not just the happy-path response.

---

Health Endpoints
/health
/ready
/live
Required.
`/ready` verifies the Guardrails Engine's dependencies (e.g. rule/pattern sources, PII detection resources) are loaded, in addition to database, cache, and vector store connectivity — a service that is "up" but cannot run Guardrails must not report ready.

---

Streaming
Use StreamingResponse for LLM outputs.
Raw provider tokens are never streamed directly to the client. Guardrails cannot evaluate hallucination, integrity, or ATS compliance on a partial response — those checks require the complete output. Stream provider tokens internally for progress/UX purposes (e.g. a "generating..." indicator or intermediate status events) but only emit the actual resume content to the client after the complete response has passed through Guardrails.
If a rejection occurs after streaming has started, the stream terminates with a structured error event, never with partial unvalidated content left in the client buffer.

---

Background Jobs
Use FastAPI BackgroundTasks only for lightweight tasks.
Heavy jobs go to workers.
Guardrail evaluation is not a "lightweight task" for BackgroundTasks — it is a required, synchronous step in the workflow before content is considered complete, not a fire-and-forget side effect.

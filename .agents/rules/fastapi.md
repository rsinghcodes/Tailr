# FastAPI Rules

Priority: HIGH

---

API Layer Responsibilities

Routes only.

No business logic.

---

Every endpoint requires

Request model

Response model

Dependency Injection

Error handling

Logging

---

Routers

One router per domain.

Example

resume.py

job.py

health.py

admin.py

---

Dependencies

Always use Depends().

Never instantiate services.

---

Responses

Always use response models.

Never return ORM objects.

---

Validation

Pydantic v2.

Strict validation.

---

Errors

Return standardized API responses.

Never expose tracebacks.

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

500 Internal Server Error

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

---

OpenAPI

Every endpoint documented.

Every schema documented.

---

Health Endpoints

/health

/ready

/live

Required.

---

Streaming

Use StreamingResponse for LLM outputs.

---

Background Jobs

Use FastAPI BackgroundTasks only for lightweight tasks.

Heavy jobs go to workers.

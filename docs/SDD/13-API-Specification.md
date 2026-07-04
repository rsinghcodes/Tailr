# API Specification

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the REST API exposed by Tailr.

The API provides access to all platform capabilities including resume management, knowledge indexing, workflow orchestration, AI optimization, ATS scoring, rendering, and analytics.

The API follows RESTful principles and exchanges JSON unless otherwise specified.

---

# 2. Design Principles

The API follows these principles.

## Resource-Oriented

Resources represent business entities.

Examples

- Resume
- Workflow
- Job Description
- ATS Report

---

## Stateless

Each request contains all required information.

No server-side session state.

---

## Versioned

Every endpoint belongs to an API version.

Example

```
/api/v1/
```

---

## Typed

Every request and response follows a schema.

---

## Explainable Errors

Every failure returns structured information.

---

# 3. API Overview

```
Client

↓

API Gateway

↓

Authentication

↓

Resume Service

Knowledge Service

Workflow Service

ATS Service

Rendering Service
```

---

# 4. Base URL

```
http://localhost:8000/api/v1
```

Production

```
https://api.tailr.ai/v1
```

---

# 5. Authentication

Version 1

JWT Bearer Token

```
Authorization

Bearer <token>
```

Future

- OAuth2
- GitHub Login
- Google Login

---

# 6. Standard Response

Success

```json
{
  "success": true,
  "data": {},
  "message": null
}
```

Failure

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Resume parsing failed."
  }
}
```

---

# 7. Resume APIs

## Upload Resume

```
POST

/resumes
```

Uploads a LaTeX resume.

Multipart Form

```
resume.tex
```

Response

```json
{
  "resume_id": "abc123",
  "status": "uploaded"
}
```

---

## List Resumes

```
GET

/resumes
```

Returns all stored resumes.

---

## Resume Details

```
GET

/resumes/{resume_id}
```

---

## Delete Resume

```
DELETE

/resumes/{resume_id}
```

---

# 8. Job Description APIs

## Analyze Job Description

```
POST

/job-descriptions
```

Request

```json
{
  "text": "..."
}
```

Response

```json
{
  "job_description_id": "...",
  "title": "...",
  "skills": []
}
```

---

## Get Parsed JD

```
GET

/job-descriptions/{id}
```

---

# 9. Knowledge APIs

## Build Knowledge Index

```
POST

/knowledge/index
```

Request

```json
{
  "resume_id": "..."
}
```

---

## Search Knowledge

```
POST

/knowledge/search
```

Request

```json
{
  "query": "FastAPI"
}
```

Response

```json
{
  "chunks": [],
  "count": 5
}
```

---

# 10. Workflow APIs

## Start Optimization

```
POST

/workflows
```

Request

```json
{
  "resume_id": "...",
  "job_description_id": "...",
  "model": "qwen3"
}
```

Response

```json
{
  "workflow_id": "...",
  "status": "PENDING"
}
```

---

## Workflow Status

```
GET

/workflows/{workflow_id}
```

Response

```json
{
  "status": "REWRITING",
  "progress": 67
}
```

---

## Cancel Workflow

```
POST

/workflows/{workflow_id}/cancel
```

---

# 11. Optimization APIs

## Generate Rewrite Plan

```
POST

/optimization/plan
```

---

## Rewrite Resume

```
POST

/optimization/rewrite
```

---

## Validate Resume

```
POST

/optimization/validate
```

---

# 12. ATS APIs

## Generate ATS Report

```
POST

/ats/analyze
```

Request

```json
{
  "resume_id": "...",
  "job_description_id": "..."
}
```

Response

```json
{
  "overall_score": 89,
  "recommendations": []
}
```

---

## Compare ATS Reports

```
GET

/ats/compare
```

---

# 13. Rendering APIs

## Generate LaTeX

```
POST

/render/latex
```

---

## Compile PDF

```
POST

/render/pdf
```

Response

```json
{
  "pdf_url": "...",
  "compile_logs": []
}
```

---

# 14. Version APIs

## List Resume Versions

```
GET

/resumes/{id}/versions
```

---

## Restore Version

```
POST

/resumes/{id}/versions/{version}/restore
```

---

# 15. Analytics APIs

## Optimization History

```
GET

/history
```

---

## Dashboard Metrics

```
GET

/analytics
```

Response

```json
{
  "total_resumes": 10,
  "average_ats_score": 86,
  "optimizations": 42
}
```

---

# 16. Health APIs

```
GET

/health
```

Returns

- API status
- Database
- Qdrant
- Ollama
- Redis

---

# 17. Error Codes

| Code             | Meaning                   |
| ---------------- | ------------------------- |
| VALIDATION_ERROR | Invalid request           |
| PARSE_ERROR      | Resume parsing failed     |
| KNOWLEDGE_ERROR  | Indexing failed           |
| WORKFLOW_ERROR   | Workflow execution failed |
| ATS_ERROR        | ATS analysis failed       |
| RENDER_ERROR     | PDF compilation failed    |
| INTERNAL_ERROR   | Unexpected server error   |

---

# 18. HTTP Status Codes

| Status | Meaning               |
| ------ | --------------------- |
| 200    | Success               |
| 201    | Resource Created      |
| 202    | Accepted              |
| 400    | Bad Request           |
| 401    | Unauthorized          |
| 403    | Forbidden             |
| 404    | Resource Not Found    |
| 409    | Conflict              |
| 422    | Validation Failed     |
| 429    | Too Many Requests     |
| 500    | Internal Server Error |

---

# 19. Rate Limiting

Default limits

```
100 requests/minute
```

AI endpoints

```
20 requests/minute
```

Limits are configurable.

---

# 20. Idempotency

The following endpoints are idempotent:

- GET
- DELETE
- Resume validation

Workflow creation supports an optional `Idempotency-Key` header to prevent duplicate optimization jobs.

---

# 21. Pagination

Collection endpoints support:

```
?page=1

&page_size=20

&sort=created_at

&order=desc
```

---

# 22. Filtering

Example

```
GET

/resumes?status=completed
```

```
GET

/history?company=OpenAI
```

---

# 23. Security

API protections include:

- JWT authentication
- HTTPS
- Request validation
- Input sanitization
- File size limits
- MIME type validation
- Rate limiting

---

# 24. OpenAPI Support

The API is fully documented using OpenAPI 3.1.

FastAPI automatically exposes:

```
/docs
```

Swagger UI

```
/redoc
```

ReDoc

---

# 25. Future APIs

Future endpoints include:

- Cover Letter Generation
- LinkedIn Optimization
- GitHub Analysis
- Interview Preparation
- Portfolio Builder
- Career Analytics
- Resume Benchmarking

The existing API version remains backward compatible.

---

# 26. Summary

The Tailr API exposes every platform capability through a versioned, resource-oriented REST interface.

By separating resume management, knowledge retrieval, workflow orchestration, ATS analysis, rendering, and analytics into dedicated services, the API remains modular, scalable, and easy to evolve.

Strong typing, structured error handling, authentication, and OpenAPI documentation ensure the API is suitable for both internal development and future third-party integrations.

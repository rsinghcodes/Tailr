# Observability Architecture

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the observability architecture for Tailr.

Observability enables developers to understand the internal behavior of the platform by collecting metrics, logs, traces, AI telemetry, and user feedback.

Unlike traditional web applications, Tailr observes not only infrastructure health but also AI reasoning quality, retrieval effectiveness, workflow execution, and user acceptance.

---

# 2. Design Goals

The observability platform must:

- Detect failures quickly
- Trace complete workflows
- Monitor LLM performance
- Measure retrieval quality
- Detect hallucinations
- Detect prompt injection attempts
- Monitor guardrail effectiveness
- Track user satisfaction
- Support production debugging
- Minimize operational overhead

---

# 3. Observability Philosophy

Tailr follows five principles.

## Everything is Observable

Every request, workflow, agent, and AI interaction should generate telemetry.

---

## Correlation First

Every event shares a common correlation ID.

This enables complete request tracing.

---

## Structured Data

Logs are JSON.

Metrics are labeled.

Traces are correlated.

---

## AI-Aware Monitoring

Monitor prompts, retrieval, guardrails, validation, and reasoning—not only APIs.

---

## Privacy by Design

Sensitive user content is never logged.

Only metadata is retained.

---

# 4. High-Level Architecture

```
                User Request
                      │
                      ▼
                 API Gateway
                      │
             Correlation ID
                      │
                      ▼
             Workflow Execution
                      │
      ┌───────────────┼─────────────────┐
      ▼               ▼                 ▼
   Metrics         Logs             Traces
      │               │                 │
      └───────────────┼─────────────────┘
                      ▼
             Observability Platform
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
 Prometheus       Grafana          Langfuse
                      │
                      ▼
            Guardrail Analytics & Alerts
```

---

# 5. Observability Components

| Component           | Purpose              |
| ------------------- | -------------------- |
| Prometheus          | Metrics collection   |
| Grafana             | Dashboards           |
| Langfuse            | LLM telemetry        |
| OpenTelemetry       | Distributed tracing  |
| Structured Logging  | Debugging            |
| Alert Manager       | Notifications        |
| Guardrail Analytics | AI safety monitoring |
| Alert Manager       | Notifications        |

---

# 6. Correlation IDs

Every request receives:

```
request_id

workflow_id

trace_id

user_id
```

These identifiers appear in:

- logs
- traces
- metrics
- workflow events

This enables complete debugging.

---

# 7. Structured Logging

Every log entry follows a common schema.

Example

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "workflow",
  "workflow_id": "wf_123",
  "request_id": "req_456",
  "trace_id": "trace_789",
  "guardrail_status": "passed",
  "message": "Rewrite completed"
}
```

Logs never contain raw resumes.

---

# 8. Log Levels

Supported levels

```
DEBUG

INFO

WARNING

ERROR

CRITICAL
```

Production disables DEBUG logging.

---

# 9. Metrics

Tailr exposes Prometheus metrics.

Examples

```
http_requests_total
workflow_duration_seconds
resume_parse_latency
llm_tokens_total
vector_search_latency
validation_failures_total
guardrail_requests_total
guardrail_failures_total
guardrail_repairs_total
prompt_injection_detected_total
hallucination_detected_total
```

Metrics are labeled.

---

# 10. API Metrics

Monitor

- Request rate
- Response time
- Error rate
- Concurrent requests
- HTTP status codes

These metrics detect infrastructure problems.

---

# 11. Workflow Metrics

Examples

- Workflow duration
- Success rate
- Retry count
- Average optimization time
- Queue depth

Each workflow stage is measured independently.

---

# 12. LLM Metrics

Important measurements

- Prompt latency
- Completion latency
- Tokens in
- Tokens out
- Context size
- Retry count
- Model utilization

These metrics identify expensive prompts.

---

# 13. Prompt Observability

Langfuse records

- Prompt version
- Model
- Temperature
- Response
- Guardrail result
- Validation result
- Token usage
- Latency
- Output repair status

Each prompt execution becomes searchable.

---

# 14. Retrieval Metrics

Measure

- Retrieval latency
- Top-K accuracy
- Chunk relevance
- Embedding generation time
- Cache hit ratio

Low retrieval quality often leads to poor rewrites.

---

# 15. Validation Metrics

Track

- Validation pass rate
- Guardrail pass rate
- Guardrail repair rate
- Hallucination detections
- Prompt injection detections
- Schema failures
- Business rule violations
- Retry frequency

Validation and guardrail trends indicate AI quality and safety.

---

# 16. ATS Metrics

Examples

- Average ATS score
- Score improvement
- Recommendation acceptance
- Missing keyword frequency

These metrics measure product value.

---

# 17. Infrastructure Metrics

Monitor

CPU

Memory

Disk

GPU

Network

Container health

These metrics support operational stability.

---

# 18. Distributed Tracing

Every workflow becomes a trace.

```
API Request

↓

Parser

↓

Knowledge Builder

↓

Retriever

↓

Planner

↓

Rewriter

↓

Guardrails

↓

Validator

↓

ATS Engine

↓

Renderer
```

OpenTelemetry propagates trace context.

---

# 19. Dashboards

Recommended Grafana dashboards

System

- CPU
- Memory
- Network

Application

- Requests
- Errors
- Latency

AI

- Tokens
- Prompt latency
- Validation rate
- Hallucination rate spike
- Prompt injection spike
- Guardrail rejection rate > 5%
- Guardrail latency increase
- Prompt latency increase
- Validation failures

Business

- ATS improvement
- Workflow success
- User activity

---

# 20. Alerts

Examples

Infrastructure

- CPU > 90%
- Memory > 85%
- Disk > 80%

Application

- Error rate > 5%
- Workflow failures
- Database unavailable

AI

- Hallucination rate spike
- Prompt latency increase
- Validation failures

Alerts should prioritize actionable issues.

---

# 21. Audit Trail

Every workflow stores

- User action
- Timestamp
- Prompt version
- Model
- Guardrail result
- Validation result
- Resume version
- ATS score
- Output repair status

Audit trails support reproducibility.

---

# 22. User Feedback Metrics

Collect

- Accepted rewrite
- Manual edits
- Rejected suggestions
- Satisfaction score

Feedback improves future prompt evaluation.

---

# 23. Retention Policy

Suggested retention

| Data             | Retention |
| ---------------- | --------- |
| Metrics          | 30 days   |
| Logs             | 90 days   |
| Traces           | 30 days   |
| Prompt telemetry | 180 days  |
| Guardrail events | 180 days  |
| Audit records    | Permanent |

Policies are configurable.

---

# 24. Security

Observability must never expose

- Resume content
- API secrets
- JWT tokens
- User passwords
- Personal identifiers

Sensitive values are masked before logging.

---

# 25. Testing

Verify

- Metrics exported
- Trace propagation
- Log format
- Dashboard queries
- Alert rules
- Guardrail metrics
- Guardrail trace correlation
- Prompt injection telemetry
- Telemetry completeness

Observability should be tested continuously.

---

# 26. Future Enhancements

Future capabilities

- AI anomaly detection
- Prompt quality trends
- Automated root cause analysis
- Workflow replay
- Predictive failure alerts
- Cost forecasting
- Multi-model comparison dashboards
- Guardrail effectiveness scoring
- Prompt injection trend analysis
- Automated hallucination clustering
- AI safety anomaly detection
- Guardrail policy drift detection

---

# 27. Architecture Decisions

| Decision                       | Rationale                             |
| ------------------------------ | ------------------------------------- |
| OpenTelemetry                  | Vendor-neutral tracing                |
| Prometheus                     | Industry-standard metrics             |
| Grafana                        | Flexible dashboards                   |
| Langfuse                       | AI-native observability               |
| Structured JSON logs           | Machine-readable debugging            |
| Correlation IDs                | End-to-end traceability               |
| Guardrail Analytics            | AI safety observability               |
| Provider-independent telemetry | Consistent monitoring across all LLMs |

---

# 28. Summary

Tailr adopts an AI-native observability architecture that combines infrastructure monitoring, distributed tracing, structured logging, LLM telemetry, and guardrail analytics.

By observing every workflow, prompt, retrieval operation, guardrail decision, validation step, and user interaction, the platform provides complete visibility into both operational health and AI safety behavior.

The observability stack enables faster debugging, safer deployments, better prompt optimization, continuous guardrail tuning, and ongoing improvement of the overall user experience while maintaining privacy-by-design principles.

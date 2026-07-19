# Deployment Architecture

**Project:** Tailr

**Version:** 1.0

**Status:** Draft

---

# 1. Purpose

This document defines the deployment architecture of Tailr.

The deployment strategy enables:

- Local development
- Free student deployment
- Production cloud deployment
- AI model hosting
- Guardrails enforcement
- Monitoring
- Automated delivery
- Horizontal scalability

The architecture follows a container-first approach using Docker.

---

# 2. Deployment Goals

The deployment architecture must:

- Run completely on a laptop
- Use open-source infrastructure
- Support GPU acceleration when available
- Be reproducible
- Support CI/CD
- Enable horizontal scaling
- Minimize operational cost
- Enforce AI safety policies consistently

---

# 3. Deployment Philosophy

Tailr follows three principles.

## Local First

Every component must run locally.

No cloud dependency.

---

## Container Native

Every service runs inside Docker.

---

## Cloud Ready

The same Docker images can be deployed to any cloud.

---

# 4. High-Level Deployment

```
                    Internet
                        │
                        ▼
                  Reverse Proxy
                   (Nginx/Traefik)
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
     Frontend        Backend       WebSocket
      (React)       (FastAPI)       Server
                        │
        ┌───────────────┼─────────────────────┐
        ▼               ▼                     ▼
 PostgreSQL         Redis               Qdrant
        │
        ▼
 Object Storage
(Local/S3)

                        │
                        ▼
                   Ollama Server
                        │
                        ▼
                Open Source LLMs
```

---

# 5. Deployment Components

Frontend

- React
- Vite

Backend

- FastAPI

AI

- Ollama
- LlamaIndex

Guardrails

- Validation & Guardrails Engine
- Prompt Injection Detection
- Hallucination Detection
- Output Repair Pipeline

Storage

- PostgreSQL
- Redis
- Qdrant

Files

- Local Storage

Monitoring

- Langfuse
- Prometheus
- Grafana

---

# 6. Docker Architecture

```
docker-compose

│

├── frontend

├── backend

├── postgres

├── qdrant

├── redis

├── ollama

├── langfuse

├── prometheus

└── grafana
```

Each service has its own Dockerfile.

---

# 7. Local Development

Student setup

```
Laptop

↓

Docker Compose

↓

All Services
```

Requirements

- Docker Desktop
- Git
- Python
- Node.js

GPU is optional.

---

# 8. Environment Variables

Example

```env
POSTGRES_URL=
QDRANT_URL=
REDIS_URL=
OLLAMA_URL=
LANGFUSE_URL=
JWT_SECRET=
STORAGE_PATH=
```

Guardrails

```env
ENABLE_GUARDRAILS=true
ENABLE_PII_VALIDATION=true
ENABLE_HALLUCINATION_CHECK=true
ENABLE_PROMPT_INJECTION_CHECK=true
ENABLE_OUTPUT_REPAIR=true
GUARDRAIL_TIMEOUT_MS=2000
GUARDRAIL_MAX_RETRIES=1
```

Secrets are never committed.

---

# 9. Networking

Docker network

```
tailr-network
```

Internal communication

```
backend

↓

postgres
```

```
backend

↓

redis
```

```
backend

↓

qdrant
```

No internal services are publicly exposed.

---

# 10. Storage Volumes

Persistent volumes

```
postgres_data

qdrant_data

redis_data

ollama_models

resume_storage

grafana_data
```

Container recreation does not lose data.

---

# 11. AI Model Deployment

Ollama hosts

- Qwen
- Llama
- Gemma

Example

````
```text
Backend

↓

Ollama API

↓

Qwen 3

↓

Raw Response

↓

Guardrails

↓

Validated Response
````

````

Models remain local.

---

# 12. Object Storage

Version 1

```text
storage/
  resumes/
  pdf/
  reports/
  guardrails/
  logs/
````

```

Future

MinIO

AWS S3

Cloudflare R2

---

# 13. Reverse Proxy

Nginx handles

- HTTPS
- Compression
- Static assets
- Rate limiting
- Request routing

Future

Traefik supports automatic service discovery.

---

# 14. HTTPS

Production

Let's Encrypt

Certificates renewed automatically.

Development

Self-signed certificates.

---

# 15. Background Jobs

Long-running tasks

- Embedding generation
- PDF compilation
- Workflow execution
- ATS scoring
- Guardrail batch validation
- Hallucination auditing

Queue

Redis

Workers

FastAPI + ARQ/Celery (future)

---

# 16. Monitoring

Application metrics

- Request latency
- API throughput
- Error rate
- Workflow duration
- Guardrail latency
- Guardrail rejection rate

Infrastructure metrics

- CPU
- RAM
- Disk
- GPU
- Network

---

# 17. AI Observability

Langfuse records

- Prompt versions
- Token usage
- Latency
- Model
- Retrieval quality
- Validation failures
- Guardrail violations
- Output repair events

---

# 18. Logging

Centralized logs

- Application
- Workflow
- Database
- LLM
- Guardrails
- Validation

Logs remain structured JSON.

---

# 19. CI/CD Pipeline

```

GitHub

↓

GitHub Actions

↓

Tests

↓

Lint

↓

Security Scan

↓

Guardrail Tests

↓

Docker Build

↓

Push Image

↓

Deploy

```

Deployment is automated after successful checks.

---

# 20. Build Pipeline

```

Frontend

↓

Vite Build

↓

Static Files

Backend

↓

Docker Image

↓

Registry

````

Validation

```text
Guardrail Test Suite

↓

Contract Validation

↓

Deployment Approval
````

---

# 21. Scaling Strategy

Current

Single instance

Future

```

Load Balancer

↓

Backend 1

Backend 2

Backend 3

```

Redis enables shared workflow state.

---

# 22. Horizontal Scaling

Stateless services

- Backend
- Frontend

Stateful services

- PostgreSQL
- Qdrant
- Redis

These require replication strategies.

---

# 23. Backup Strategy

Daily backups

- PostgreSQL
- Guardrail audit tables

Weekly snapshots

- Qdrant

Persistent storage

- Resume files
- Guardrail reports

Backups are automated.

---

# 24. Disaster Recovery

Recover

- Database
- Vector index
- Resume files
- Guardrail audit logs
- Configuration

Target Recovery Time Objective

< 30 minutes

---

# 25. Security

Deployment security

- HTTPS
- JWT
- Docker secrets
- Non-root containers
- Read-only file systems
- Firewall rules
- Prompt injection protection
- PII protection
- Guardrail enforcement
- Structured output validation

Sensitive data remains encrypted.

---

# 26. Performance Targets

| Component            | Target  |
| -------------------- | ------- |
| API latency          | <200 ms |
| Resume parsing       | <500 ms |
| Retrieval            | <100 ms |
| ATS analysis         | <5 s    |
| Resume optimization  | <30 s   |
| PDF generation       | <5 s    |
| Guardrail validation | <2 s    |

---

# 27. Production Deployment

Recommended infrastructure

Frontend

Vercel

Backend

Railway / Render / Fly.io

Database

Neon PostgreSQL

Vector DB

Qdrant Cloud (Free Tier)

Storage

Cloudflare R2

Models

Ollama (GPU VM) or vLLM

This minimizes operational cost while preserving full AI observability and guardrail enforcement.

---

# 28. Kubernetes Roadmap

Future deployment

```

Ingress

↓

Frontend

↓

Backend Deployment

↓

Redis

↓

PostgreSQL

↓

Qdrant

↓

GPU Inference Pods

```

Helm charts simplify deployment.

---

# 29. Infrastructure as Code

Future

Terraform

Docker Compose

Helm

Infrastructure becomes reproducible.

---

# 30. Deployment Environments

Development

Local Docker

Testing

GitHub Actions

Staging

Cloud

Production

Cloud + Monitoring

Each environment has isolated configuration and guardrail policies.

---

# 31. Architecture Decisions

| Decision                     | Rationale                                  |
| ---------------------------- | ------------------------------------------ |
| Docker                       | Consistent environments                    |
| Docker Compose               | Simple local setup                         |
| Ollama                       | Free local inference                       |
| PostgreSQL                   | ACID persistence                           |
| Qdrant                       | Semantic retrieval                         |
| Redis                        | Caching and workflow state                 |
| Langfuse                     | LLM observability                          |
| Nginx                        | Reverse proxy and HTTPS                    |
| Guardrails Layer             | Provider-independent AI safety enforcement |
| Structured output validation | Deterministic downstream processing        |

---

# 32. Summary

Tailr adopts a container-first deployment architecture that supports both local development and production-scale deployments.

By combining Docker, FastAPI, PostgreSQL, Redis, Qdrant, Ollama, a dedicated Guardrails layer, and modern observability tooling, the platform remains reproducible, scalable, secure, and cost-effective.

The architecture enables students to run the complete AI stack on a laptop while providing a clear migration path to cloud-native production deployments with enterprise-grade AI governance, structured validation, prompt injection protection, hallucination detection, and comprehensive deployment observability.

```

```

# Architecture Rules

Priority: CRITICAL

These rules override implementation preferences.

---

# Architecture

Tailr uses:

- Domain Driven Design (DDD)
- Hexagonal Architecture
- Clean Architecture
- SOLID Principles
- Twelve-Factor App

Never violate these principles.

---

# Dependency Direction

Dependencies MUST point inward.

Allowed

API
↓
Application
↓
Domain
↓
Interfaces
↓
Infrastructure

Forbidden

Infrastructure → Domain

Infrastructure → API

API → Infrastructure

Application → FastAPI

Domain → SQLAlchemy

---

# Layer Responsibilities

## app/

Only application startup.

Allowed

- FastAPI
- lifespan
- middleware
- startup
- shutdown

Forbidden

Business logic

Repositories

LLMs

Database queries

---

## api/

Responsible only for HTTP.

Allowed

- validation
- serialization
- dependency injection
- authentication
- authorization

Forbidden

SQL

LLM

Redis

Qdrant

Business logic

---

## application/

Coordinates business use cases.

Allowed

Repositories

Providers

Domain Services

Events

Transactions

Forbidden

HTTP

FastAPI

SQLAlchemy models

Prompt templates

---

## domain/

Contains business knowledge.

Allowed

Entities

Value Objects

Policies

Business Rules

Domain Services

Forbidden

FastAPI

SQLAlchemy

HTTP

Redis

Ollama

Qdrant

---

## infrastructure/

Implements interfaces.

Allowed

Database

Redis

Vector DB

Ollama

HTTP Clients

Filesystem

Storage

Forbidden

Business Rules

Workflow orchestration

Prompt engineering

---

# Ports & Adapters

Every external dependency must be abstracted.

Correct

ResumeRepository

↓

PostgresResumeRepository

Wrong

Application

↓

SQLAlchemy

---

# Provider Pattern

Application

↓

LLMProvider

↓

OllamaProvider

↓

OpenAIProvider

↓

HFProvider

Never import Ollama directly.

---

# Repository Pattern

Repositories only perform persistence.

Never

Generate prompts

Call LLMs

Validate business rules

---

# Service Pattern

Application Services coordinate work.

Repositories persist.

Providers integrate.

Entities contain behavior.

Keep responsibilities separated.

---

# Prompt Rules

Prompt templates belong only inside

backend/prompts/

Never inline prompts inside Python.

---

# AI Agents

Each agent has exactly one responsibility.

Never combine agents.

Never let agents call each other directly.

Only workflows coordinate agents.

---

# Workflows

Only LangGraph workflows orchestrate.

Agents never orchestrate.

---

# RAG

Pipeline

Parser

↓

Chunker

↓

Embedding

↓

Retriever

↓

Reranker

↓

Prompt Builder

↓

Generator

↓

Validator

Never merge stages.

---

# Domain Model

Business rules belong inside:

Entities

Domain Services

Policies

Never inside routers.

Never inside repositories.

---

# Dependency Injection

Always inject interfaces.

Never instantiate dependencies manually.

---

# Configuration

Everything configurable.

Never hardcode.

Always use Settings.

---

# Scalability

Every component should be replaceable.

Every provider should have an interface.

Never couple implementation details.

---

# Anti Patterns

Never

SQL in routers

Prompt generation in services

LLM in repositories

Redis in domain

Business logic in middleware

Global state

Circular imports

God classes

Utility classes

Shared mutable state

---

# Architecture Validation

Before generating code verify:

✓ Layer correct
✓ Dependency direction correct
✓ Interface exists
✓ Replaceable implementation
✓ Testable

If any answer is NO,

redesign before coding.

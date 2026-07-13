# Architecture Guide

> Project: Tailr
> Version: 1.0
> Status: Production

---

# Purpose

This document defines the official software architecture for Tailr.

Every implementation must follow this architecture.

If an implementation conflicts with this document, this document takes precedence.

---

# Guiding Principles

Tailr is designed as a long-term production system.

Architecture decisions prioritize:

- Maintainability
- Scalability
- Testability
- Replaceability
- Separation of Concerns
- Low Coupling
- High Cohesion

Never optimize for writing less code.

Always optimize for writing better software.

---

# Architectural Style

Tailr combines:

- Domain Driven Design (DDD)
- Hexagonal Architecture
- Clean Architecture
- SOLID Principles
- Twelve-Factor App

These are complementary, not competing.

---

# High-Level Architecture

                  ┌──────────────────────┐
                  │     Frontend         │
                  └──────────┬───────────┘
                             │
                        REST API
                             │
                  ┌──────────▼───────────┐
                  │      API Layer       │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │  Application Layer   │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │    Domain Layer      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │ Infrastructure Layer │
                  └──────────────────────┘

Dependencies always point downward.

Business rules always point upward.

---

# Project Structure

backend/

app/

api/

application/

domain/

infrastructure/

shared/

telemetry/

config/

agents/

workflows/

prompts/

---

# Layer Responsibilities

## app/

Responsible only for application startup.

Contains:

FastAPI factory

Middleware registration

Lifespan

Startup

Shutdown

Never contains business logic.

---

## api/

Responsible for HTTP only.

Allowed:

Routing

Validation

Dependency Injection

Authentication

Serialization

Forbidden:

Database access

Prompt creation

Business rules

LLM calls

Repository implementation

---

## application/

Coordinates use cases.

Examples:

Tailor Resume

Generate Cover Letter

Analyze Job Description

Create Embeddings

Application layer orchestrates work.

Application layer does not contain infrastructure code.

---

## domain/

Contains business knowledge.

Examples:

Entities

Value Objects

Business Rules

Policies

Domain Services

Domain layer must never import FastAPI.

Domain layer must never import SQLAlchemy.

Domain layer must never import HTTP clients.

---

## infrastructure/

Implements interfaces.

Contains:

Database

Redis

Qdrant

Ollama

LlamaIndex

Storage

HTTP clients

No business rules belong here.

---

## shared/

Reusable building blocks.

Exceptions

Schemas

Enums

Utilities

Pagination

Response Models

Types

Shared code should have no business meaning.

---

## telemetry/

Logging

Metrics

Tracing

Observability

Monitoring

Cross-cutting concerns only.

---

# Dependency Direction

Correct

API

↓

Application

↓

Domain

↓

Ports

↓

Infrastructure

Wrong

Infrastructure

↓

Application

Domain

↓

API

Repositories

↓

Routers

---

# Ports & Adapters

Every external dependency must be abstracted.

Example

Application

↓

ResumeRepository

↓

PostgresRepository

Never inject SQLAlchemy directly into services.

---

# Provider Pattern

Every AI model must be hidden.

Application

↓

LLMProvider

↓

OllamaProvider

↓

OpenAIProvider

↓

HFProvider

Application never knows which provider is used.

---

# Vector Store Pattern

Application

↓

VectorStore

↓

Qdrant

↓

FAISS

↓

Chroma

Never call Qdrant directly from services.

---

# Repository Pattern

Repositories only perform persistence.

Repositories must never:

Call LLMs

Generate prompts

Perform validation

Contain workflows

Repositories should be replaceable.

---

# Service Pattern

Application Services coordinate work.

They:

Validate business rules

Call repositories

Call providers

Return domain objects

They should never:

Execute SQL

Build HTTP responses

Call FastAPI directly

---

# Domain Model

Entities contain behavior.

Bad

Resume

name

skills

experience

Good

Resume

calculate_score()

remove_duplicates()

normalize_skills()

Business logic belongs inside entities or domain services.

---

# AI Agent Architecture

Every AI agent must have exactly one responsibility.

Planner

↓

Resume Analyzer

↓

JD Analyzer

↓

Retriever

↓

Writer

↓

ATS Validator

↓

Critic

↓

Optimizer

↓

Final Validator

Agents communicate through structured interfaces.

Agents never call each other directly.

---

# LangGraph Workflow

Workflows coordinate agents.

Planner

↓

Retrieve

↓

Generate

↓

Validate

↓

Critique

↓

Rewrite

↓

Score

↓

Complete

Only workflows orchestrate agents.

---

# RAG Architecture

Document

↓

Parser

↓

Chunker

↓

Embedding Model

↓

Vector Store

↓

Retriever

↓

Reranker

↓

Prompt Builder

↓

LLM

↓

Structured Output

Every stage must be replaceable.

---

# Configuration

No hardcoded values.

Everything configurable.

Environment variables

Typed settings

Validation at startup

---

# Dependency Injection

Never instantiate dependencies manually.

Correct

Service

↓

Repository Interface

↓

Implementation

Wrong

service = ResumeService()

inside a router.

---

# Error Handling

Every layer raises typed exceptions.

API converts exceptions into HTTP responses.

Never expose internal stack traces.

---

# Logging

Every important operation logs:

Start

End

Duration

Failure

Request ID

Module

Never use print().

---

# Testing Strategy

Every layer is independently testable.

Unit Tests

↓

Application

↓

Repository

↓

API

↓

Integration Tests

Mock infrastructure.

Never mock business logic.

---

# Security

Validate all inputs.

Validate uploaded files.

Never trust AI output.

Never trust external APIs.

Escape user content.

Protect secrets.

---

# Scalability

System must support:

Horizontal scaling

Multiple AI providers

Multiple vector databases

Background workers

Streaming responses

Distributed tracing

Future microservice extraction

without major refactoring.

---

# Anti-Patterns

Never place SQL inside routers.

Never call Ollama inside API routes.

Never create prompts inside services.

Never use global database sessions.

Never expose SQLAlchemy models outside repositories.

Never couple domain to infrastructure.

Never use synchronous I/O.

Never use print().

Never introduce circular imports.

---

# Architecture Review Checklist

Every Pull Request must answer:

Does this respect DDD?

Does this respect Hexagonal Architecture?

Are dependencies pointing inward?

Is infrastructure replaceable?

Is business logic isolated?

Are interfaces used?

Can this module be tested independently?

If any answer is NO,

the implementation should be redesigned.

---

# Final Principle

Architecture is more important than implementation.

A feature can always be rewritten.

A bad architecture becomes permanent.

Protect the architecture first.

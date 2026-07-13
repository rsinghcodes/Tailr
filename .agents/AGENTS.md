# AGENTS.md

> Master Engineering Guide for AI Coding Agents
>
> Project: Tailr
> Version: 1.0
> Status: Production
> Last Updated: 2026-07-12

---

# Purpose

This repository contains the source code for **Tailr**, an AI-powered resume tailoring platform.

This file defines how AI coding agents must behave while working on this repository.

Every AI assistant MUST read this file before making changes.

This file has higher priority than generic coding knowledge.

---

# Mission

Build production-quality software.

Do not build tutorial code.

Do not generate placeholder implementations.

Do not sacrifice architecture for simplicity.

Every change should be deployable.

---

# Product Vision

Tailr enables job seekers to create ATS-optimized resumes by combining:

- Resume Parsing
- Job Description Analysis
- Retrieval-Augmented Generation (RAG)
- Multi-Agent AI
- ATS Validation
- Resume Rewriting
- Resume Scoring

---

# High-Level Architecture

Tailr follows:

- Domain Driven Design (DDD)
- Hexagonal Architecture
- Clean Architecture principles
- Ports & Adapters
- SOLID
- Twelve-Factor App

Dependencies always point inward.

Infrastructure never contains business logic.

---

# Tech Stack

## Backend

Python 3.13

FastAPI

SQLAlchemy 2.x Async

Alembic

PostgreSQL

Redis

Qdrant

LlamaIndex

LangGraph

Ollama

Pydantic v2

HTTPX

OpenTelemetry

Prometheus

## Frontend

Next.js

React

TypeScript

Tailwind CSS

TanStack Query

Zustand

ShadCN UI

React Hook Form

Zod

---

# Primary Design Principles

1. Simplicity over cleverness.

2. Explicit over implicit.

3. Composition over inheritance.

4. Async first.

5. Business logic belongs only inside the Domain/Application layers.

6. Infrastructure is replaceable.

7. Every external dependency must be abstracted.

8. Every module must be independently testable.

9. Every public API must be typed.

10. Never introduce technical debt intentionally.

---

# Project Structure

backend/

    app/
    api/
    config/
    telemetry/
    shared/
    domain/
    application/
    infrastructure/
    agents/
    workflows/
    prompts/

frontend/

docs/

.agents/

---

# Layer Responsibilities

## app/

FastAPI bootstrap only.

Contains:

- middleware
- startup
- shutdown
- lifespan
- app factory

No business logic.

---

## api/

Responsible only for HTTP.

Allowed:

- request validation

- response serialization

- dependency injection

Forbidden:

- SQL

- AI

- repositories

- prompt generation

- business rules

---

## application/

Coordinates business use cases.

Can call:

- repositories

- providers

- domain services

Cannot access FastAPI directly.

---

## domain/

Contains:

- entities

- value objects

- domain services

- business rules

Must not import infrastructure.

---

## infrastructure/

Contains:

- PostgreSQL

- Redis

- Qdrant

- Ollama

- LlamaIndex

- HTTP clients

Everything here is replaceable.

---

## shared/

Reusable components.

Examples:

Exceptions

Enums

Schemas

Utilities

Response models

Types

Pagination

---

## telemetry/

Logging

Metrics

Tracing

Request IDs

Correlation IDs

OpenTelemetry

No business logic.

---

# Dependency Rule

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

Infrastructure

↓

Application

Domain

↓

FastAPI

Application

↓

SQLAlchemy Models

Repositories

↓

Routers

---

# AI Provider Rules

Never call an LLM directly.

Always use a Provider abstraction.

Example

Application

↓

LLMProvider Interface

↓

OllamaProvider

OpenAIProvider

HFProvider

---

# Vector Database Rules

Never import Qdrant directly.

Always use:

VectorStore interface

Implementations:

Qdrant

FAISS

Chroma

---

# Repository Rules

Repositories only perform persistence.

Repositories never:

Generate prompts

Call LLMs

Contain business logic

Repositories should be replaceable.

---

# Prompt Rules

Prompt templates belong only in:

prompts/

Never inline prompts inside Python code.

Prompt versions must be tracked.

---

# Agent Rules

Every AI Agent:

Has a single responsibility.

Produces structured output.

Can be tested independently.

Can fail independently.

Never depends directly on another agent implementation.

Communication happens through interfaces.

---

# Workflow Rules

Workflow orchestration belongs only inside:

workflows/

Individual agents never orchestrate other agents.

---

# Error Handling

Never expose raw exceptions.

Always raise typed exceptions.

All exceptions must map to standardized API responses.

---

# Logging Rules

No print().

Use the telemetry package.

All logs must be structured.

Every request must include:

Request ID

Correlation ID

Duration

Module

Operation

---

# Security Rules

Validate every external input.

Never trust uploaded files.

Never trust LLM output.

Escape HTML.

Sanitize filenames.

Validate MIME types.

Protect secrets.

Never log credentials.

Never commit API keys.

---

# Performance Rules

Avoid N+1 queries.

Batch embeddings.

Reuse HTTP clients.

Connection pooling enabled.

Cache frequently used prompts.

Stream LLM output when appropriate.

---

# Testing Rules

Every feature requires:

Unit tests

Integration tests

Edge case tests

Failure tests

Regression tests

No feature is complete without tests.

---

# Documentation Rules

Every public class requires documentation.

Every exported function requires type hints.

Architecture decisions require an ADR.

Large features require engineering documentation.

---

# Code Quality Rules

Maximum function length:

60 lines

Maximum class length:

300 lines

Cyclomatic complexity:

<10 preferred

Avoid deep nesting.

Prefer early returns.

---

# Code Generation Rules

AI assistants MUST:

Read AGENTS.md first.

Read relevant ADRs.

Read architecture documents.

Understand the feature.

Design before coding.

Generate production-ready code.

Generate tests.

Explain trade-offs.

Never invent APIs.

Never fabricate requirements.

Never remove existing architecture without justification.

---

# Definition of Done

A task is complete only if:

✓ Code builds

✓ Tests pass

✓ Ruff passes

✓ MyPy passes

✓ Documentation updated

✓ Architecture preserved

✓ Logging added

✓ Error handling implemented

✓ Dependency injection used

✓ No TODO placeholders

---

# When Unsure

Do not guess.

Ask for clarification.

Or stop and explain the architectural conflict.

Incorrect production code is worse than incomplete code.

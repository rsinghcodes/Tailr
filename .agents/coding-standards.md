# Coding Standards

> Project: Tailr
> Version: 1.0
> Status: Production

---

# Purpose

This document defines the official coding standards for Tailr.

Every AI coding agent must follow these standards.

Every Pull Request will be reviewed against this document.

When standards conflict with personal preferences,
this document always wins.

---

# Philosophy

Code is read far more often than it is written.

Optimize for readability.

Optimize for maintainability.

Optimize for correctness.

Never optimize for writing fewer lines.

---

# Python Version

Python 3.13

Do not write compatibility code for older versions.

Use modern Python features whenever they improve clarity.

Examples:

✓ match statements

✓ | union types

✓ pathlib

✓ dataclasses when appropriate

✓ StrEnum

✓ slots

---

# Formatting

Formatting is automatic.

Never manually align code.

Tools:

Ruff

Black

isort (via Ruff)

---

# Line Length

Maximum:

88 characters

Exceptions only when readability improves.

---

# Naming

## Variables

Good

resume_id

job_description

embedding_model

Bad

x

temp

obj

data1

---

## Functions

Use verbs.

Good

calculate_score()

generate_embeddings()

validate_resume()

parse_document()

Bad

score()

process()

handle()

---

## Classes

Use nouns.

Good

ResumeService

JobAnalyzer

ResumeRepository

EmbeddingProvider

Bad

Manager

Utils

Helper

Processor

---

## Constants

UPPER_CASE

MAX_FILE_SIZE

DEFAULT_TIMEOUT

VECTOR_DIMENSION

---

## Modules

snake_case.py

Never CamelCase filenames.

---

# Imports

Order

Standard Library

↓

Third Party

↓

Internal

Separate groups with one blank line.

Never use wildcard imports.

Bad

from utils import \*

Good

from utils.parser import ResumeParser

---

# Type Hints

Every public function must have type hints.

Bad

def create(data):

Good

def create(data: ResumeRequest) -> Resume:

Return types are mandatory.

---

# Docstrings

Public classes

Public functions

Public modules

must have docstrings.

Use Google Style.

Example

def generate_embeddings(text: str) -> list[float]:
"""
Generate embeddings.

    Args:
        text:
            Input text.

    Returns:
        Vector embedding.
    """

---

# Function Rules

Maximum length

60 lines

Maximum parameters

5

Maximum nesting

3

Prefer early return.

Bad

if a:

    if b:

        if c:

Good

if not a:

    return

if not b:

    return

---

# Class Rules

Maximum

300 lines

Single responsibility.

If class has multiple responsibilities,

split it.

---

# Comments

Comment WHY.

Never comment WHAT.

Bad

# increment i

i += 1

Good

# Retry to handle transient provider failures

---

# Async

Backend is async-first.

Database

Async

HTTP

Async

Redis

Async

LLM

Async

Never block the event loop.

Forbidden

requests

time.sleep

subprocess.run()

Allowed

httpx.AsyncClient

asyncio.sleep()

---

# Error Handling

Never catch Exception unless re-raising.

Bad

except Exception:

Good

except ValidationError:

except ProviderError:

except DatabaseError:

---

# Exceptions

Use typed exceptions.

Every layer has its own exception types.

Never raise RuntimeError.

Never raise generic Exception.

---

# Logging

Never use print().

Always use

logging.getLogger(**name**)

Use structured logging.

Every log should contain useful context.

Bad

logger.info("Done")

Good

logger.info(

    "Resume parsed",

    extra={

        "resume_id": resume.id,

        "duration_ms": duration,

    },

)

---

# Configuration

Never hardcode values.

Use Settings.

Bad

timeout = 30

Good

timeout = settings.HTTP_TIMEOUT

---

# FastAPI

Routes must be thin.

Good

Router

↓

Application Service

↓

Repository

Bad

Router

↓

SQLAlchemy

↓

LLM

↓

Redis

---

# Dependency Injection

Never instantiate services manually.

Bad

service = ResumeService()

Good

Depends(get_resume_service)

---

# SQLAlchemy

Always use SQLAlchemy 2.x style.

Use async sessions.

Never use session.query().

Use select().

Never expose ORM models outside repositories.

---

# Pydantic

Use Pydantic v2.

Separate:

Request

Response

Internal

schemas.

Do not reuse request models as database models.

---

# Repositories

Repositories only persist data.

Forbidden

Validation

AI

Business rules

Prompt generation

---

# Services

Services coordinate work.

They should:

Validate business rules.

Call repositories.

Call providers.

Return domain objects.

---

# Providers

Providers communicate with external systems.

Examples

Ollama

OpenAI

Qdrant

Redis

S3

Providers never contain business logic.

---

# AI Prompts

Prompt templates belong in

prompts/

Never inline prompts.

Every prompt requires versioning.

---

# AI Output

Never trust LLM output.

Always validate.

Retry when appropriate.

Handle malformed JSON.

Use structured outputs whenever possible.

---

# RAG

Every stage separated.

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

Never combine stages.

---

# Testing

Every feature requires

Unit Tests

Integration Tests

Edge Cases

Failure Cases

Regression Tests

No exceptions.

---

# Performance

Avoid N+1 queries.

Reuse clients.

Cache expensive operations.

Batch embeddings.

Use pagination.

Never load unnecessary data.

---

# Security

Validate uploads.

Validate MIME types.

Validate file size.

Escape HTML.

Protect secrets.

Never log credentials.

Never expose stack traces.

---

# Code Smells

Avoid

God Classes

Utility Classes

Global State

Circular Imports

Duplicate Logic

Deep Nesting

Long Functions

Magic Numbers

Hardcoded Strings

---

# Refactoring

Refactor when

Readability improves

Complexity decreases

Architecture improves

Do not refactor purely for style.

---

# Definition of Clean Code

A module is clean when

It has one responsibility.

It is independently testable.

It is typed.

It is documented.

It follows architecture.

It contains no duplication.

It contains no dead code.

It contains meaningful logs.

It handles failures correctly.

---

# Before Every Commit

Run

ruff check .

ruff format .

mypy .

pytest

Fix every warning.

Do not ignore issues.

---

# Final Rule

Write code that another senior engineer
can understand in five minutes.

If that is not possible, rewrite it.

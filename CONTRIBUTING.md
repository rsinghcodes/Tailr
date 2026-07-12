# Contributing to Tailr

First off, thank you for taking the time to contribute!

Tailr is an open-source AI engineering project focused on building a trustworthy, explainable, and production-ready resume optimization platform using Multi-Agent AI, RAG, and modern software engineering practices.

Whether you're fixing bugs, improving documentation, adding new AI capabilities, or optimizing performance, your contributions are greatly appreciated.

---

# Table of Contents

- Code of Conduct
- Ways to Contribute
- Development Workflow
- Project Setup
- Branch Naming
- Commit Messages
- Pull Request Process
- Coding Standards
- Testing
- Documentation
- Reporting Issues
- Security

---

# Code of Conduct

Please be respectful and professional.

We strive to build an inclusive and welcoming community.

By participating, you agree to:

- Be respectful.
- Be constructive.
- Provide helpful feedback.
- Assume good intentions.
- Keep discussions professional.

---

# Ways to Contribute

You can contribute by:

- Fixing bugs
- Improving documentation
- Adding tests
- Improving AI prompts
- Optimizing RAG retrieval
- Enhancing ATS scoring
- Supporting additional LaTeX templates
- Improving frontend UX
- Performance optimization
- Security improvements
- Developer tooling

---

# Development Workflow

1. Fork the repository

2. Clone your fork

```bash
git clone https://github.com/<your-username>/tailr.git
```

3. Create a new branch

```bash
git checkout -b feature/amazing-feature
```

4. Make your changes

5. Run tests

6. Commit

7. Push

8. Open a Pull Request

---

# Local Development

## Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Infrastructure

```bash
docker compose up -d
```

This starts

- PostgreSQL
- Redis
- Ollama

---

# Branch Naming

Please follow the convention below.

## Features

```text
feature/resume-parser
```

```text
feature/rag-retriever
```

---

## Bug Fixes

```text
fix/parser-crash
```

---

## Documentation

```text
docs/update-readme
```

---

## Refactoring

```text
refactor/database-layer
```

---

## Tests

```text
test/parser-tests
```

---

# Commit Messages

Use Conventional Commits.

Examples

```text
feat(parser): support nested latex commands

fix(rag): resolve duplicate chunk retrieval

docs(readme): update installation guide

refactor(database): simplify repository pattern

test(parser): add tokenizer unit tests
```

---

# Pull Requests

Please ensure your PR:

- Has a clear description
- Solves one logical problem
- Passes all tests
- Includes documentation updates if required
- Follows project coding standards

Small pull requests are preferred over large ones.

---

# Coding Standards

## Python

- Python 3.12+
- Type hints required
- Follow PEP 8
- Use Ruff
- Use MyPy
- Prefer async APIs
- Keep functions focused
- Avoid global state

---

## TypeScript

- Enable strict mode
- Prefer functional components
- Avoid `any`
- Use reusable components
- Keep business logic separate from UI

---

# Architecture Principles

Please follow the project's architecture.

- Clean Architecture
- Repository Pattern
- Dependency Injection
- Multi-Agent Design
- RAG-first Retrieval
- Domain-driven organization

Business logic should never depend directly on frameworks.

---

# Testing

Every contribution should include appropriate tests whenever applicable.

Examples

- Unit tests
- Integration tests
- API tests
- Parser tests
- Validation tests

Run tests before opening a PR.

Backend

```bash
pytest
```

Frontend

```bash
npm test
```

---

# Documentation

If your change affects:

- APIs
- Architecture
- Configuration
- Workflows
- AI Agents

please update the corresponding documentation inside the `docs/` directory.

---

# Reporting Issues

When opening an issue, please include:

- Expected behavior
- Actual behavior
- Steps to reproduce
- Logs (if available)
- Screenshots (if applicable)
- Environment details

---

# Security

Please **do not** disclose security vulnerabilities publicly.

Instead, contact the maintainers privately so the issue can be investigated and fixed responsibly.

---

# Project Philosophy

Tailr is built on five guiding principles:

- Never fabricate resume content.
- The master resume is the source of truth.
- Every AI decision should be explainable.
- Prefer deterministic systems over prompt-only solutions.
- Build software that is production-ready, testable, and maintainable.

---

# Recognition

Every meaningful contribution is appreciated.

Thank you for helping make Tailr better! 🚀

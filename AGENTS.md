# AGENTS.md

Guidance for AI coding agents working in the Tailr monorepo. Read this before editing code.

## Repository layout

- `apps/backend/` — Python FastAPI service (the API). Not a classic flat FastAPI app; it uses a layered/clean architecture (see below).
- `apps/frontend/` — Next.js 16 app. **Read `apps/frontend/AGENTS.md` before writing frontend code** — this is Next.js 16, which has breaking changes vs. older versions, and it is explicitly NOT the Next.js from common training data.
- `.github/workflows/ci.yml` — CI pipeline. Run the same checks locally.
- `docker-compose.yml` — runs **Redis only** (Postgres and Qdrant are external/cloud).
- `netlify.toml` — frontend deploys to Netlify.

## Backend

### Commands (from CI, run in `apps/backend/`)

```sh
pip install -r requirements-dev.txt          # runtime + dev deps
ruff check .                                  # lint
mypy . --ignore-missing-imports || true       # type check (non-blocking in CI)
pytest -v --tb=short                          # tests (CI sets continue-on-error)
uvicorn main:app --reload                     # dev server
```

- CI and the Dockerfile use **Python 3.12**. Local `.venv` may be 3.13; prefer 3.12 for parity.
- `requirements.txt` is intentionally stripped to 17 pinned runtime deps. Do not add `--no-deps` installs; pin exact versions to avoid pip resolver backtracking.
- Entrypoint is `apps/backend/main.py`: `from app.app import create_app; app = create_app()`.

### Configuration

- `config/settings.py` (pydantic-settings, `case_sensitive=True`, reads `.env`) requires `DATABASE_URL` and `GEMINI_API_KEY`. Copy `apps/backend/.env.example` to `.env` for defaults.
- Key defaults: `API_PREFIX=/api/v1`, `GEMINI_MODEL=gemini-3.6-flash`, `QDRANT_COLLECTION=tailr-documents`, CORS allows `http://localhost:3000`.
- On startup, `app/lifespan.py` runs readiness checks against PostgreSQL, Redis, Qdrant, and Gemini. All four services are required; the app logs warnings for offline services but does not crash.

### Architecture

Layered structure, follow existing patterns when adding code:

- `api/routes/` — FastAPI routers + `api/routes/*_schemas.py`. Everything lives under `/api/v1`.
- `application/` — use-case services (`auth/`, `resume/`, `job_description/`, `workflow/`, `guardrails/`).
- `domain/` — entities, repositories, shared exceptions (`domain/shared/`).
- `infrastructure/` — adapters: `database/` (SQLAlchemy async), `redis/`, `langchain/` (LLM provider + health), `llamaindex/` (parser, extractors, vector store), `repositories/`.
- `workflows/` — LangGraph pipeline (state → nodes → graph): `retrieve_context → plan → rewrite → guardrails → validation → ats_analysis → render`.
- `guardrails/` — custom guardrail engine (`base.py`, `pipeline.py`) with profiles `rewrite_strict`, `analysis_standard`, `validation_paranoid` and validators in `guardrails/validators/`.
- `validators/` — additional validation engine (`engine.py`, `citation_validator.py`, `rule_validator.py`).
- `prompts/` — versioned prompt templates in subfolders with `metadata.yaml` and `system_v1.txt`/`user_v1.txt`; registry at `prompts/registry.py`.
- `telemetry/` — structured logging (request context, filters, formatters).
- `alembic/` — migrations; currently a single squashed initial migration (`73cab716e7e3_initial.py`).

### Key dependencies (pinned, `requirements.txt`)

- `fastapi[standard]==0.140.7`, `uvicorn[standard]==0.30.0`, `pydantic==2.13.4`, `SQLAlchemy`, `alembic`, `asyncpg`, `psycopg2-binary`
- `langchain==0.3.18`, `langchain-google-genai==2.0.4`, `langgraph==0.2.60` (pinned; do not bump to langchain 1.x — `langchain-google-genai` 2.x and `langgraph` 0.2.x depend on the 0.3.x line)
- `qdrant-client==1.18.0`, `redis`, `llama-cloud==2.13.0`, `python-jose`, `bcrypt`, `python-json-logger`

### Auth

- JWT via `python-jose`, passwords hashed with `bcrypt`. Router dependency in `api/dependencies/auth.py`.
- Frontend stores the token in `localStorage["tailr_token"]` and sends `Authorization: Bearer`.

## Frontend

See `apps/frontend/AGENTS.md` (already in-repo) — read it before touching frontend code. Key scripts (run in `apps/frontend/`):

```sh
npm run dev          # local dev server
npm run build        # production build
npm run lint         # eslint
npm run type-check   # tsc --noEmit
```

- API base from `NEXT_PUBLIC_API_BASE` (default `http://localhost:8000/api/v1`); production is `https://tailr-qxn1.onrender.com/api/v1` via `netlify.toml`.
- `NEXT_PUBLIC_API_BASE` is an `env.local`-style build-time var; set it before `npm run build`.

## Testing

- No `apps/backend/tests/` directory currently exists; CI runs `pytest` with `continue-on-error: true`.
- Frontend has no test runner configured (lint + type-check + build only).

## Gotchas

- `models/gemini-embedding-001` in `infrastructure/llamaindex/vector_store.py` embeds to **3072 dims** — Qdrant collection dimension must match.
- `docker-compose.yml` starts Redis only; Postgres and Qdrant must be provided externally (check `apps/backend/.env` for URLs).
- When changing pinned dependency versions, verify against CI Python 3.12, not a local 3.13 venv.
- Working tree is usually kept clean on `dev`; don't leave `.env` or `tsconfig.tsbuildinfo` staged (`.gitignore` already covers them).

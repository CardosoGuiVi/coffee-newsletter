# CLAUDE.md

This file guides Claude Code when working in this repository.
Full documentation lives in [`docs/`](docs/README.md).

---

## Project Overview

Coado is an automated weekly specialty coffee newsletter (PT-BR).
It combines a FastAPI subscription API with a pipeline that scrapes RSS feeds,
summarizes content via Claude API, and delivers emails via Resend.

Stack: Python 3.12, FastAPI, SQLAlchemy 2.0 async, Neon (PostgreSQL), AWS Lambda, Vercel.

---

## Commands

```bash
# Development
uv sync                  # install dependencies
make db-up               # start local Postgres (docker compose)
make db-down             # stop local Postgres
make fastapi-dev         # API at http://localhost:8000 (depends on db-up)
make db-migrate          # alembic upgrade head
make db-revision msg="..." # new migration (msg required)

# Build & Deploy
make build-layer         # rebuild lambda layer (only when deps change)
make build-function      # copy apps/ and packages/ to .build/function/
make deploy              # sam build + sam deploy (runs build-function automatically)

# Quality
make check               # lint-ci + typecheck (CI quality gate)
make lint                # ruff format + check --fix (autofix)
make typecheck           # uv run mypy packages/ apps/
make pre-commit          # lint + typecheck + pre-commit run --all-files
pytest                   # run all tests (needs Postgres → make db-up)
pytest tests/unit/       # unit tests only
pytest tests/integration/ # integration tests only
```

---

## Repository Structure

```
apps/
├── api/                  ← FastAPI entrypoint (routes, schemas, dependencies)
├── web/                  ← Static frontend (Vercel)
└── newsletter_pipeline/  ← Weekly pipeline entrypoint
packages/
├── ai/                   ← Anthropic Claude API integration
├── core/                 ← Shared config (Pydantic Settings, COFFEE_ prefix)
├── database/             ← SQLAlchemy base, models, repositories, Alembic
├── mailer/               ← Mailer protocol + Resend implementation
├── newsletter/           ← Domain logic, templates, prompts
└── scraper/              ← RSS collection
```

---

## Architecture Rules

### Layer responsibilities
- `apps/` contains entrypoints only — routes, dependency wiring, HTTP concerns
- `packages/` contains all domain logic and infrastructure implementations
- Never add business logic, SQL queries, or provider-specific code inside `apps/`

### Services
- Services orchestrate workflows, call repositories and providers
- Services raise **domain exceptions** (e.g. `EmailAlreadySubscribed`)
- Services never raise `HTTPException` or return HTTP responses
- Routes in `apps/api/` convert domain exceptions into HTTP responses

### Repositories
- Repositories handle data access only — ORM queries, persistence
- Repositories receive `AsyncSession` via dependency injection
- Repositories never call external providers or contain business logic

### Providers
- Use Protocol-based abstractions for all external providers
- Business logic depends on protocols, never on concrete implementations
- Example: `Mailer` protocol → `ResendMailer` implementation

### Dependency injection
- Prefer constructor-based injection
- Never instantiate infrastructure dependencies internally inside services

---

## Configuration

- Root `Settings` class in `packages/core/config.py`
- Uses `pydantic-settings` with `COFFEE_` prefix and `__` as nested delimiter
- Example: `COFFEE_DATABASE__HOST` → `settings.DATABASE.HOST`
- Nested `BaseSettings` instances use `env_nested_delimiter="__"` on the parent

---

## Testing Conventions

- **Always use PostgreSQL** — never SQLite, even for unit tests
- Use Protocol-based fakes for providers: `FakeMailer`, `FakeAI`
- Tests live in `tests/unit/` and `tests/integration/`
- Fixtures in `tests/fixtures/`, fakes in `tests/fakes/`
- Report proposed changes before applying them

```
tests/
├── conftest.py
├── fakes/
│   ├── fake_mailer.py
│   └── fake_ai.py
├── fixtures/
├── unit/
│   └── services/
└── integration/
```

---

## Infrastructure

| Component | Platform | Notes |
|---|---|---|
| API | AWS Lambda (`sa-east-1`) | SAM, Mangum adapter, Function URL |
| Database | Neon (PostgreSQL) | Free tier, connection pooler enabled |
| Frontend | Vercel | `main` → production (`coado.club`) |
| Pipeline | GitHub Actions | Mondays 07:17 UTC (temporary, moving to EventBridge) |
| Layer | `coado-dependencies` | Managed by SAM via `template.yaml` |

---

## Git Workflow

- `main` → production (`coado.club`)
- `development` → active work
- Feature branches cut from `development`
- Prefer `--force-with-lease` over `--force`
- Small, frequent commits — ensure stable checkpoints especially with Claude Code

---

## Before Making Changes

1. Read the relevant `docs/` file before touching unfamiliar code
2. Report what you plan to change and why — wait for confirmation before applying
3. Prefer small isolated changes over large refactors
4. When in doubt about architecture decisions, check `docs/architecture/decisions.md`

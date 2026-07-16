<div align="center">
  <img src="apps/web/images/logo-dark.svg" alt="Coado Logo" width="400"/>

  <p>An automated weekly newsletter about coffee (PT-BR). It collects news from global RSS feeds, summarizes them with the Claude API, and delivers them by email.</p>

  ![CI](https://github.com/CardosoGuiVi/coffee-newsletter/actions/workflows/ci.yml/badge.svg)
  [![codecov](https://codecov.io/gh/CardosoGuiVi/coffee-newsletter/graph/badge.svg)](https://codecov.io/gh/CardosoGuiVi/coffee-newsletter)
  [![Vercel](https://img.shields.io/badge/Vercel-deployed-000000?logo=vercel&logoColor=white)](https://coado.club)
  ![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-deployed-FF9900?logo=awslambda&logoColor=white)

</div>

# ☕ Coado

**Status:** 🟢 In production · Weekly automation via GitHub Actions

🌐 **Live:** [coado.club](https://coado.club)

---

## What it is

A fullstack project combining:

- **Signup site + API** — a static frontend (Vercel) talking to a FastAPI service
  (AWS Lambda) that manages subscriptions and exposes public stats.
- **Automation pipeline** — RSS scraper → Claude API → Resend email delivery,
  running weekly on GitHub Actions.

It is deliberately built as something simple (a coffee newsletter) on top of a
robust, modular architecture — the stack is where the learning happens.

## Architecture in one breath

A **modular monolith** in a monorepo: `apps/` holds thin entrypoints, `packages/`
holds all reusable domain and infrastructure logic.

```
coffee-newsletter/
├── apps/
│   ├── api/                  ← FastAPI app (routes, schemas, dependencies)
│   ├── web/                  ← Static frontend (hosted on Vercel)
│   └── newsletter_pipeline/  ← Weekly pipeline entrypoint
├── packages/
│   ├── ai/                   ← Claude API integration
│   ├── core/                 ← Shared config (Pydantic Settings)
│   ├── database/             ← SQLAlchemy base, sessions, models, repositories, Alembic migrations
│   ├── mailer/               ← Mail provider abstractions (Resend, ...)
│   ├── newsletter/           ← Newsletter domain logic, templates, prompts
│   └── scraper/              ← RSS collection and scraping
├── pyproject.toml            ← Dependencies (uv)
├── Makefile · compose.yaml · template.yaml · alembic.ini
```

📚 **Full documentation lives in [`docs/`](docs/README.md):**

- [Architecture overview](docs/architecture/overview.md)
- [Architecture decisions](docs/architecture/decisions.md) — why AWS Lambda, why no
  agent frameworks, why a cron over a worker
- [Packages](docs/architecture/packages.md)
- [Getting started](docs/development/getting-started.md)
- [Environment variables](docs/development/environment.md)
- [Deployment](docs/infrastructure/deployment.md)
- [Pipeline](docs/infrastructure/pipeline.md)

## Quick start

```bash
git clone git@github.com:CardosoGuiVi/coffee-newsletter.git
cd coffee-newsletter
uv sync
cp .env.example .env        # then edit with your credentials
make fastapi-dev            # API at http://localhost:8000 (routes under /v1/)
```

To run the static frontend locally:

```bash
cd apps/web && python3 -m http.server 8080
```

See [getting started](docs/development/getting-started.md) for pointing the
frontend at the local API.

## Tech stack

| Area      | Tools                                                             |
|-----------|------------------------------------------------------------------|
| Language  | Python 3.12, uv                                                  |
| Backend   | FastAPI, SQLAlchemy 2.0 async, asyncpg, Alembic, Pydantic v2     |
| Email     | Resend, Jinja2 templates                                        |
| AI        | Anthropic Claude API (`claude-haiku-4-5`)                        |
| Frontend  | Vanilla HTML/CSS/JS                                              |
| Infra     | AWS Lambda (API, SAM), Neon (PostgreSQL), Vercel, GitHub Actions |
| Local dev | Docker Compose (PostgreSQL), Makefile                           |
| Quality   | ruff, mypy, pre-commit, Dependabot                              |

## Deployment

| Component | Platform       | Trigger                              |
|-----------|----------------|--------------------------------------|
| API       | AWS Lambda (sa-east-1) | SAM — `make deploy`          |
| Frontend  | Vercel         | `main` → production, others → preview |
| Pipeline  | GitHub Actions | Cron — Mondays 07:17 UTC (04:17 BRT) |

The frontend reaches the API through a Vercel rewrite proxy (`/v1/*` → Lambda Function URL),
so the browser stays on one origin and there is no CORS to manage. Details in
[deployment](docs/infrastructure/deployment.md).

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the current short-, medium-, and long-term
plan. In short: tests and security hardening next, applied-AI topics (embeddings,
RAG, vector DBs) further out.

## License

MIT — see [LICENSE](LICENSE).

---

**Maintained by:** Guilherme Cardoso
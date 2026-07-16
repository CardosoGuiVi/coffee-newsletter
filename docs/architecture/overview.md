# Architecture Overview

Coado follows a **modular monolith** architecture organized as a monorepo. The
guiding principle is a strict separation between *entrypoints* (`apps/`) and
*reusable logic* (`packages/`).

## The core rule

- **`apps/` contains entrypoints only.** Applications wire dependencies,
  bootstrap services, expose HTTP routes, and execute workflows. They do not
  contain business logic, SQL queries, infrastructure implementations, or
  orchestration logic.
- **`packages/` contains reusable domain and infrastructure code.** All
  newsletter business logic, mail providers, AI integrations, database setup,
  repositories, and scraping logic live here.

This keeps `main.py` files minimal and makes the domain logic testable without
any framework.

## Repository layout

```
coffee-newsletter/
│
├── apps/
│   ├── api/                  ← FastAPI app: routes, schemas, dependencies
│   ├── web/                  ← Static frontend (HTML, CSS, JS, assets)
│   └── newsletter_pipeline/  ← Pipeline entrypoint and orchestration
│
├── packages/
│   ├── ai/                   ← Claude API integration, LLM clients
│   ├── core/                 ← Shared config (Pydantic Settings), constants
│   ├── database/             ← SQLAlchemy base, sessions, models, repositories, Alembic migrations
│   ├── mailer/               ← Mail provider abstractions (Resend, SES, ...)
│   ├── newsletter/           ← Newsletter domain logic, schemas, templates
│   └── scraper/              ← RSS collection and scraping logic
│
├── pyproject.toml            ← Dependencies (uv)
├── Makefile                  ← Useful commands
├── compose.yaml              ← Docker (PostgreSQL)
├── template.yaml             ← AWS SAM infra (Lambda)
└── alembic.ini               ← Alembic config
```

## Layer responsibilities

| Layer                  | Responsibility                                                        |
|------------------------|----------------------------------------------------------------------|
| `apps/api`             | FastAPI routes, dependencies, API schemas, HTTP concerns             |
| `apps/web`             | Static multi-page frontend (signup, unsubscribe, legal, error pages), served by Vercel |
| `apps/newsletter_pipeline` | Orchestration entrypoint for the weekly run                     |
| `packages/newsletter`  | Newsletter domain: campaign/subscription workflows, rendering, prompts |
| `packages/database`    | SQLAlchemy models, sessions, repositories, migrations                |
| `packages/mailer`      | Mail provider abstractions and implementations                       |
| `packages/ai`          | AI provider integrations and LLM clients                             |
| `packages/scraper`     | RSS collection, source definitions, scraping logic                   |
| `packages/core`        | Shared configuration via Pydantic Settings                           |

## Services and repositories

**Services** are the orchestration layer. They may coordinate workflows, call
repositories, call providers, and apply business rules. They must **not** return
HTTP responses, raise `HTTPException`, or know anything about the web framework.
When something goes wrong, a service raises a *domain* exception (for example
`EmailAlreadySubscribed`), and the route layer translates it into the correct
HTTP response.

**Repositories** are responsible for database access only — ORM queries and
persistence. They receive an `AsyncSession` via dependency injection and avoid
framework coupling. They do not contain business workflows or call external
providers.

## Dependency injection and abstractions

Dependencies are injected through constructors rather than created internally:

```python
class CampaignService:
    def __init__(
        self,
        subscriber_repository: SubscriberRepository,
        mailer: Mailer,
    ):
        ...
```

External providers sit behind `Protocol`-based abstractions, so the domain
depends on contracts rather than concrete SDKs:

```python
from typing import Protocol

class Mailer(Protocol):
    async def send_email(self, ...) -> None: ...
```

This is what makes provider swapping (Resend → SES, Anthropic → another LLM)
and testing with fakes possible without touching domain code.

## Two runtime surfaces

The same packages power two different entrypoints:

1. **The API** (`apps/api`) — runs continuously on Railway, handling signups and
   serving public stats.
2. **The pipeline** (`apps/newsletter_pipeline`) — runs on a schedule via GitHub
   Actions, not as a long-running service.

Both compose the same domain and infrastructure packages; only the entrypoint
and lifecycle differ. See the [pipeline doc](../infrastructure/pipeline.md) for
the weekly flow.
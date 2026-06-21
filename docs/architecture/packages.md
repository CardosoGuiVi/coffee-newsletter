# Packages

Every reusable piece of logic lives under `packages/`. Each package has a single,
well-defined responsibility and depends on abstractions rather than concrete
implementations where it crosses a boundary.

## `packages/core`

Shared configuration and constants. Centralizes all settings via Pydantic
Settings in `config.py`, so both the API and the pipeline read from one source of
truth. Provider-specific settings load from their own `env_prefix` (for example
`ANTHROPIC_*`).

Avoid duplicating configuration in the apps — they import from here.

## `packages/database`

Database setup and access: the SQLAlchemy declarative base, async sessions,
models, and repositories. Migrations are managed with Alembic.

Database access is centralized here. Direct ORM usage outside repositories or
services is avoided — repositories receive an `AsyncSession` via dependency
injection and expose persistence operations to the domain.

### Current schema

```
subscribers
├── id (UUID)
├── email (String, UNIQUE)
├── subscribed (Boolean)
├── created_at (DateTime)
└── unsubscribed_at (DateTime, nullable)
```

## `packages/newsletter`

The business domain. This is where the project's actual rules live: campaign
workflows, subscription workflows, rendering, summarization orchestration,
prompts, newsletter schemas, and domain exceptions.

Email templates live close to the domain, under
`packages/newsletter/templates/` (`newsletter.html`, `newsletter_item.html`,
`welcome.html`), rather than in a global template folder.

## `packages/mailer`

Mail provider abstractions and their implementations. The domain depends on a
`Mailer` protocol, not on a concrete provider, so Resend can be swapped for SES
or Postmark without touching business logic.

```python
from typing import Protocol

class Mailer(Protocol):
    async def send_email(self, ...) -> None: ...
```

## `packages/ai`

AI provider integrations and LLM clients. Keeps the Anthropic SDK (and any future
provider) isolated behind an abstraction so domain logic is not directly coupled
to a specific vendor's client. Summarization uses `claude-haiku` for cost
efficiency.

## `packages/scraper`

RSS collection: source definitions and scraping logic using `feedparser`. Kept
isolated from newsletter orchestration — the scraper knows how to fetch and parse
feeds, but nothing about how the newsletter is assembled or sent.

### RSS sources

**Brazilian:** Revista Espresso, CeCafé, Revista Cafeicultura, Blog do Café,
Coffee & Joy Blog, r/CafeEspecialBR.

**International:** Perfect Daily Grind, Daily Coffee News, Sprudge, Fresh Cup,
SCA News, Barista Magazine, Coffee Chronicler.

## Dependency direction

The flow of dependencies is one-directional: apps depend on packages, and within
packages the domain (`newsletter`) depends on abstractions (`mailer`, `ai`)
rather than their implementations. Infrastructure packages never reach back into
the domain.
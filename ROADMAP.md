# 🗺️ Roadmap

Where Coado is and where it's going. This tracks the real state of the project —
done, in progress, and planned.

## ✅ Done

### Signup site + API
- FastAPI app with REST endpoints (`/v1/`)
- PostgreSQL with Alembic migrations
- Email validation via Pydantic
- Deployed on Railway (single replica)
- Branding and visual identity (Coado design system: colors, Fraunces + Inter,
  logo, decorative elements)
- Frontend moved to Vercel with a rewrite proxy to the Railway API
- Custom domain `coado.club` with automatic SSL
- Rate limiting on endpoints (`slowapi`)
- CORS allowlist (`CORSMiddleware`) and trusted-host validation
  (`TrustedHostMiddleware`)
- Security response headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options,
  Referrer-Policy, Permissions-Policy)

### Automation pipeline
- RSS scraper (`feedparser`) over Brazilian + international sources
- Claude API summarization (`claude-haiku`)
- Jinja2 email rendering (table-based, inline CSS, Gmail dark-mode handling)
- Resend delivery
- Scheduled weekly via GitHub Actions (Mondays 11:00 UTC)

### Architecture & quality
- Migrated to a modular monolith (monorepo: `apps/` + `packages/`)
- Domain logic separated from infrastructure
- Protocol-based abstractions for providers (mailer, AI)
- Pydantic Settings provider abstraction layer (`packages/core/config.py`)
- ruff, mypy, pre-commit, Dependabot
- Technical documentation under `docs/`

## 🚧 In progress

- **AI provider abstraction refactor** (`refactor/configs`) — finishing the
  Pydantic Settings provider layer and merging into `dev`
- **Testing** — unit tests for services, integration tests for endpoints
  (see below)
- **Branding refinement** — minor polish; reconsidering the tagline so it doesn't
  box in future brand evolution

## 🎯 Planned

### Short term
- Test suite with meaningful coverage (services 80%+, endpoints 70%+)
- CI running tests on GitHub Actions
- Periodic security review (audit headers/CORS config, dependencies, secrets)

### Medium term
- Open/click statistics
- Subject-line experiments
- Basic subscriber analytics

### Long term
- Subscriber segments
- Multi-language support

## 🧪 Testing plan

Tests do not exist yet; this is the intended structure. Services are designed to
be testable without FastAPI, using dependency injection and Protocol-based
provider abstractions so providers can be swapped for fakes.

```
tests/
├── conftest.py              ← shared fixtures
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   └── services/
│       ├── test_subscriber_service.py
│       └── test_newsletter_service.py
└── integration/
    ├── test_subscribe_endpoint.py
    ├── test_stats_endpoint.py
    └── test_unsubscribe_endpoint.py
```

Setup:

```bash
uv add --group dev pytest pytest-asyncio pytest-cov httpx
uv run pytest --cov
```

## 🧭 Study direction

This project is a vehicle for consolidating Tier 1 backend skills before moving
into applied AI. Once it stabilizes, the next focus is foundational applied AI —
embeddings, RAG, streaming, vector databases — and later more advanced areas
(MCP, fine-tuning). Agentic patterns are intentionally deferred; the pipeline is
deterministic orchestration by design, not an agent.
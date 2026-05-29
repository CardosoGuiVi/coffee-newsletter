<div align="center">
  <img src="apps/web/images/logo-dark.svg" alt="Coffee Newsletter Logo" width="400"/>
</div>

# ☕ Coado — Newsletter about Coffees

An automated weekly newsletter about specialty coffee. Collects news from global RSS feeds, summarizes with Claude API, and sends to your audience via email.

**Status:** Live on Railway · Weekly automation via GitHub Actions

🌐 **Live:** [coffee.guicardoso.dev.br](https://coffee.guicardoso.dev.br)

---

## 📋 What It Is

A fullstack project that combines:

- **Signup website** — FastAPI → PostgreSQL subscription management
- **Automation pipeline** — RSS scraper → Claude API → Resend email delivery
- **Deployment** — Railway + Vercel + GitHub Actions

---

## 🏗️ Architecture

This project follows a **modular monolith** architecture using a monorepo-style structure.

```
coffee-newsletter/
│
├── apps/
│   ├── api/                          ← FastAPI web app (routes, schemas, dependencies)
│   ├── web/                          ← Static frontend (HTML, CSS, JS, assets)
│   │   └── images/
│   │       └── logo-dark.svg
│   └── newsletter_pipeline/          ← Pipeline entrypoint and orchestration
│
├── packages/
│   ├── ai/                           ← Claude API integration
│   ├── core/                         ← Shared config (Pydantic Settings), constants
│   ├── database/                     ← SQLAlchemy base, sessions, models, migrations
│   ├── mailer/                       ← Mail provider abstractions (Resend, SES, etc.)
│   ├── newsletter/                   ← Newsletter domain logic, schemas, templates
│   │   └── templates/
│   │       └── emails/
│   │           ├── newsletter.html
│   │           ├── newsletter_item.html
│   │           └── welcome.html
│   └── scraper/                      ← RSS feed collection and scraping logic
│
├── migrations/                       ← Alembic database versioning
│   └── versions/
│
├── pyproject.toml                    ← Dependencies (uv)
├── Makefile                          ← Useful commands
├── compose.yaml                      ← Docker (PostgreSQL)
├── railway.toml                      ← Deploy configuration
└── alembic.ini                       ← Alembic config
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| `apps/` | Entrypoints only — wire dependencies, bootstrap services, expose routes |
| `packages/newsletter` | Newsletter domain logic, campaign workflows, rendering, prompts |
| `packages/database` | SQLAlchemy models, sessions, repositories, migrations |
| `packages/mailer` | Mail provider abstractions and implementations |
| `packages/ai` | AI provider integrations and LLM clients |
| `packages/scraper` | RSS collection, source definitions, scraping logic |
| `packages/core` | Shared configuration via Pydantic Settings |

---

## 🔄 Newsletter Pipeline

### How it works

```
GitHub Actions (Monday, 8am UTC-3)
  ↓
apps/newsletter_pipeline/
  ├── packages/scraper     → Collects RSS feeds (10+ coffee sources)
  ├── packages/ai          → Claude API summarizes articles
  ├── packages/newsletter  → Jinja2 renders email template
  └── packages/mailer      → Resend sends to all subscribers
```

### RSS Sources

**Brazilian:** Revista Espresso, CaféPoint, Tudo Sobre Café, Revista Cafeicultura, Blog do Café

**International:** Perfect Daily Grind, Daily Coffee News, Sprudge, Fresh Cup, SCA News

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker (optional, for running PostgreSQL locally)
- [Make](https://www.gnu.org/software/make/) for simplified commands

### 1. Clone and setup

```bash
git clone git@github.com:CardosoGuiVi/coffee-newsletter.git
cd coffee-newsletter
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:

```env
# Database
COFFEE_DATABASE__HOST=localhost
COFFEE_DATABASE__PORT=5432
COFFEE_DATABASE__USER=local_user
COFFEE_DATABASE__DB=local_db
COFFEE_DATABASE__PASSWORD=local_password

# Anthropic API
COFFEE_ANTHROPIC_API_KEY=sk-ant-...

# Resend Email
COFFEE_RESEND_API_KEY=re_...
COFFEE_FROM_EMAIL=newsletter@your-domain.com
```

### 4. Run locally

**Option A — With Docker (recommended)**

```bash
make fastapi-dev
```

This executes:
1. `docker compose up -d database` (PostgreSQL)
2. Runs Alembic migrations automatically
3. Starts FastAPI at `http://localhost:8000`

**Option B — Without Docker (requires external PostgreSQL)**

```bash
uv run --env-file .env fastapi dev
```

---

## 📊 Database

### Migrations with Alembic

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description of change"

# Apply migrations
uv run alembic upgrade head

# Check current status
uv run alembic current
```

### Current Schema

```sql
subscribers
├── id (UUID)
├── email (String, UNIQUE)
├── subscribed (Boolean)
├── created_at (DateTime)
└── unsubscribed_at (DateTime, nullable)
```

---

## 🐳 Docker & Compose

```bash
# Start database
make db-up

# Stop database
make db-down

# View logs
docker compose logs database
```

---

## 🚀 Deployment

| Service | Target | Notes |
|---|---|---|
| API | Railway | Auto-deploys from GitHub, runs migrations on startup |
| Web | Vercel | Static frontend |
| Pipeline | GitHub Actions | Scheduled every Monday 8am UTC-3 |

**Railway start command (`railway.toml`):**

```toml
[deploy]
startCommand = "uv run fastapi run --port $PORT"
```

**Required environment variables in Railway:**
- `DATABASE_URL` (auto-generated)
- `ANTHROPIC_API_KEY`
- `RESEND_API_KEY`
- `FROM_EMAIL`
- `SECRET_KEY`

---

## ✅ Phase Status

### Phase 1 — Signup Website ✅

- [x] FastAPI app with REST endpoints
- [x] PostgreSQL with Alembic migrations
- [x] Responsive HTML frontend
- [x] Email validation with Pydantic
- [x] Deployed on Railway
- [ ] Branding and UI/UX improvements

### Phase 2 — Automation Pipeline ✅

- [x] RSS scraper working
- [x] Claude API integrated
- [x] Email renderer with Jinja2
- [x] Resend API integrated
- [x] GitHub Actions scheduled (Monday 8am)
- [x] First successful run!
- [ ] Improve quality, add tests

### Phase 3 — Refactor (In Progress)

- [x] Migrated to modular monolith (monorepo-style)
- [x] Separated domain logic from infrastructure
- [x] Protocol-based abstractions for providers
- [ ] Unit and integration tests
- [ ] Rate limiting and security hardening

---

## 🔐 Security

### Implemented

- [x] Environment variables via `.env`
- [x] Email validation
- [x] Database constraints
- [x] SQL injection prevention (via SQLAlchemy ORM)

### Planned

- [ ] Rate limiting on endpoints
- [ ] CSRF protection
- [ ] Security headers
- [ ] CORS review

---

## 🧪 Tests (Planned)

```
tests/
├── unit/
│   ├── services/
│   ├── repositories/
│   └── schemas/
├── integration/
│   ├── test_endpoints.py
│   └── test_pipeline.py
└── conftest.py
```

Services are designed to be testable without FastAPI, using dependency injection and Protocol-based abstractions for provider swapping.

---

## 🛠️ Useful Commands

```bash
# Install dependencies
uv sync

# Run app with hot-reload
make fastapi-dev

# Run pipeline manually
uv run --env-file .env python apps/newsletter_pipeline/main.py

# Lint
uv run ruff check .

# Type check
uv run mypy .

# Run tests (when available)
uv run pytest
```

---

## 📈 Roadmap

### Short term

- [ ] UI/UX improvements on the web app
- [ ] Unit and integration tests
- [ ] Rate limiting

### Medium term

- [ ] Open/click statistics dashboard
- [ ] Subject line A/B testing
- [ ] Basic analytics

### Long term

- [ ] Multi-language support
- [ ] Subscriber segments
- [ ] Marketing tool integrations

---

## 📚 References

- [FastAPI](https://fastapi.tiangolo.com)
- [SQLAlchemy](https://docs.sqlalchemy.org/20/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Anthropic API](https://docs.anthropic.com/)
- [Resend](https://resend.com/docs)
- [uv](https://docs.astral.sh/uv/)

---

## 📝 License

MIT — see [LICENSE](LICENSE)

---

**Maintained by:** Guilherme Cardoso  
**Last updated:** May 2026  
**Status:** 🟢 In production
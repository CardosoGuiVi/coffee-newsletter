# ☕ Coffee Newsletter

An automated weekly newsletter about specialty coffee. Collects news from global RSS feeds, summarizes with Claude API, and sends to your audience via email.

**Status:** Live on Railway · Weekly automation via GitHub Actions · Phase 1 + 2 in progress

🌐 **Live:** [coffee.guicardoso.dev.br](https://coffee.guicardoso.dev.br)

---

## 📋 What It Is

A fullstack project that combines:

- **Phase 1:** Simple signup website (FastAPI → PostgreSQL)
- **Phase 2:** Automation pipeline (RSS scraper → Claude API → Resend)
- **Deployment:** Railway + GitHub Actions

## 🏗️ Architecture

```
coffee-newsletter/
│
├── app/                          ← FastAPI web app
│   ├── api/v1/                   ← REST endpoints
│   ├── core/                     ← Configuration and database
│   │   ├── config.py             ← Pydantic Settings
│   │   ├── database.py           ← SQLAlchemy + asyncpg
│   │   ├── dependencies.py       ← Dependency injection
│   │   └── consts.py             ← Global constants
│   ├── models/                   ← SQLAlchemy ORM
│   │   └── newsletter.py         ← Subscriber model
│   ├── schemas/                  ← Pydantic schemas
│   │   └── newsletter.py         ← Request/response shapes
│   ├── services/                 ← Business logic
│   │   ├── subscriber.py         ← Subscriber CRUD
│   │   └── newsletter.py         ← Newsletter service
│   ├── static/                   ← Frontend assets
│   │   ├── index.html
│   │   ├── js/
│   │   └── styles/
│   └── main.py                   ← FastAPI entrypoint
│
├── pipeline/                     ← Newsletter automation
│   ├── main.py                   ← Orchestrator
│   ├── scraper.py                ← RSS feeds
│   ├── summarizer.py             ← Claude API
│   ├── sender.py                 ← Resend API
│   ├── renderer.py               ← HTML template engine
│   └── schemas/
│       ├── scraper.py
│       └── summarizer.py
│
├── migrations/                   ← Alembic (database versioning)
│   └── versions/
│       └── f51f0d54897f_subscriber_model.py
│
├── templates/                    ← Jinja2 email templates
│   ├── emails/
│   │   ├── newsletter.html       ← Main newsletter
│   │   ├── newsletter_item.html  ← Individual item
│   │   └── welcome.html          ← Welcome email
│   └── web/
│
├── pyproject.toml                ← Dependencies (uv)
├── Makefile                      ← Useful commands
├── compose.yaml                  ← Docker (PostgreSQL)
├── railway.toml                  ← Deploy configuration
├── alembic.ini                   ← Alembic config
├── run_pipeline.py               ← Pipeline runner script
└── README.md                     ← This file
```

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
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/coffee_newsletter

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Resend Email
RESEND_API_KEY=re_...
FROM_EMAIL=newsletter@your-domain.com

# Admin (security)
ADMIN_EMAIL=your@email.com
SECRET_KEY=your-secret-key-here
```

### 4. Run locally

**Option A — With Docker (recommended)**

```bash
make fastapi-dev
```

This executes:
1. `docker compose up -d database` (PostgreSQL)
2. Runs migrations automatically
3. Starts FastAPI at `http://localhost:8000`

**Option B — Without Docker (needs external PostgreSQL)**

```bash
uv run --env-file .env fastapi dev
```

<!-- ### 5. Test the endpoints

```bash
# Subscribe
curl -X POST http://localhost:8000/api/v1/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@email.com"}'

# Get stats
curl http://localhost:8000/api/v1/stats

# Unsubscribe
curl -X POST http://localhost:8000/api/v1/unsubscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@email.com"}'
``` -->

---

## 🔄 Newsletter Pipeline

### How it works

```
GitHub Actions (Monday, 8am UTC-3) 
  ↓
pipeline/main.py
  ├── scraper.py     → Collects RSS feeds (10+ coffee sources)
  ├── summarizer.py  → Claude API summarizes articles
  ├── renderer.py    → Jinja2 renders email template
  └── sender.py      → Resend sends to subscribers
```

### Run pipeline manually

```bash
uv run --env-file .env run_pipeline.py
```

Or directly:

```bash
uv run --env-file .env python pipeline/main.py
```

### RSS Sources (Configured in `app/core/consts.py`)

**Brazilian:**
- Revista Espresso, CaféPoint, Tudo Sobre Café, Revista Cafeicultura, Blog do Café

**International:**
- Perfect Daily Grind, Daily Coffee News, Sprudge, Fresh Cup, SCA News

---

## 📊 Database

### Migrations with Alembic

**Create new migration**

```bash
uv run alembic revision --autogenerate -m "description of change"
```

**Apply migrations**

```bash
uv run alembic upgrade head
```

**Check status**

```bash
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

### Database

```bash
# Start
make db-up

# Stop
make db-down

# Logs
docker compose logs database
```

### Compose Variables

Specified in `.env`:
```env
COFFEE_DATABASE__POSTGRES_USER=coffee_user
COFFEE_DATABASE__POSTGRES_PASSWORD=strong-password
COFFEE_DATABASE__POSTGRES_DB=coffee_newsletter
```

---

## 🚀 Deployment

### Railway (in production)

**Automatic deployment**
- Connected to GitHub
- Runs migrations automatically
- Triggers pipeline via webhook/schedule

**Configuration in `railway.toml`:**
```toml
[deploy]
startCommand = "uv run fastapi run --port $PORT"
```

**Variables in Railway**
- DATABASE_URL (auto-generated)
- ANTHROPIC_API_KEY
- RESEND_API_KEY
- FROM_EMAIL
- SECRET_KEY

---

## ✅ Phase Status

### Phase 1 — Signup Website ✅

- [x] FastAPI app with REST endpoints
- [x] SQLite → PostgreSQL migrations
- [x] Responsive HTML frontend
- [x] Form + real-time stats
- [x] Email validation with Pydantic
- [x] Deployed on Railway
- ⏳ **Next:** Branding and UI/UX improvements

### Phase 2 — Automation Pipeline ✅

- [x] RSS scraper working
- [x] Claude API integrated
- [x] Email renderer with Jinja2
- [x] Resend API integrated
- [x] GitHub Actions scheduled (Monday 8am)
- [x] First successful run!
- ⏳ **Next:** Improve quality, add tests

---

## 🔐 Security (In progress)

### Implemented

- [x] Environment variables via `.env`
- [x] Email validation
- [x] Database constraints
- [x] CORS (needs review)

### To do

- [ ] Rate limiting on endpoints
- [ ] CSRF protection
- [ ] Security headers
- [ ] SQL injection prevention (done via SQLAlchemy ORM)
- [ ] Security tests

---

## 🧪 Tests (To do)

### Planned structure

```
tests/
├── unit/
│   ├── services/
│   ├── models/
│   └── schemas/
├── integration/
│   ├── test_endpoints.py
│   └── test_pipeline.py
└── conftest.py
```

<!-- ### Run tests

```bash
uv add --group dev pytest pytest-asyncio pytest-cov
uv run pytest
``` -->

---

## 🎨 Branding (In progress)

### Checklist

- [ ] Coffee Newsletter logo
- [ ] Consistent color palette (already have brown/coffee)
- [ ] Improved font stack
- [ ] Design system in templates
- [ ] Email signature branding
- [ ] Newsletter header visual

---

## 📈 Next Steps (Roadmap)

### Short term (1-2 weeks)

- [ ] Improve website UI/UX
- [ ] Add unit tests
- [ ] Implement rate limiting
- [ ] Improve API documentation

### Medium term (1 month)

- [ ] Dashboard for open/click statistics
- [ ] Segment management
- [ ] Subject line A/B testing
- [ ] Basic analytics

### Long term

- [ ] Mobile app
- [ ] Affiliate system
- [ ] Marketing tool integrations
- [ ] Multi-language support

---

## 🛠️ Development

### Useful commands

```bash
# Install dependencies
uv sync

# Run app with hot-reload
make fastapi-dev

# Run pipeline
uv run python pipeline/main.py

# Check types (if mypy available)
uv run mypy app/

# Linter (if ruff available)
uv run ruff check app/

# Tests (when available)
uv run pytest
```

### Code structure

- **Models:** SQLAlchemy ORM in `app/models/`
- **Schemas:** Pydantic in `app/schemas/` (validation)
- **Services:** Business logic in `app/services/`
- **API:** Endpoints in `app/api/v1/`
- **Pipeline:** Scripts in `pipeline/`

---

## 📚 Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com) — Framework
- [SQLAlchemy](https://docs.sqlalchemy.org/20/) — ORM
- [Alembic](https://alembic.sqlalchemy.org/) — Migrations
- [Pydantic](https://docs.pydantic.dev/) — Validation
- [Anthropic API](https://docs.anthropic.com/) — Claude
- [Resend](https://resend.com/docs) — Email

---

## 📝 License

MIT (see LICENSE)

---

**Maintained by:** Guilherme Cardoso  
**Last updated:** May 2026  
**Status:** 🟢 In production
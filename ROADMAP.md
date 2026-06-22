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
- Scheduled weekly via GitHub Actions (Mondays 07:17 UTC = 04:17 BRT) — cron
  moved from peak-hour `0 11` to off-peak `17 7` to avoid queue delays

### Architecture & quality
- Migrated to a modular monolith (monorepo: `apps/` + `packages/`)
- Domain logic separated from infrastructure
- Protocol-based abstractions for providers (mailer, AI)
- Pydantic Settings provider abstraction layer (`packages/core/config.py`)
- ruff, mypy, pre-commit, Dependabot
- Technical documentation under `docs/`
- Unit tests for `SubscriptionService` (`tests/unit/services/`)

## 🚧 In progress

- **AI provider abstraction refactor** (`refactor/configs`) — finishing the
  Pydantic Settings provider layer and merging into `dev`
- **Testing** — unit tests for services done; integration tests for endpoints
  still pending
- **Branding refinement** — minor polish; reconsidering the tagline so it doesn't
  box in future brand evolution

## 🎯 Planned

### Short term
- Test suite with meaningful coverage (services 80%+, endpoints 70%+)
- CI running tests on GitHub Actions
- Periodic security review (audit headers/CORS config, dependencies, secrets)
- **Repository bug fixes** (identified in code review):
  - `soft_delete()` incorrectly overwrites `created_at`, corrupting original join
    date and inflating `joined_this_week` stats
  - `update()` (re-subscribe) also resets `created_at`, same impact on stats
  - `unregister()` missing guard for already-unsubscribed state — double call
    resets the 30-day cooldown clock
  - Redundant `db.refresh()` in `soft_delete()` (returns `None`, extra round-trip)
  - `stats()` runs two sequential queries with a TOCTOU window — collapse into
    single query with conditional aggregation

### Medium term
- Open/click statistics
- Subject-line experiments
- Basic subscriber analytics

### Infrastructure migration
Ordered steps — each is independent and does not require the next to be done first.

**Step 1 — Migrate database to Neon** *(low effort)*
- Provision Neon PostgreSQL (free tier)
- Run Alembic migrations against Neon
- Update Railway env vars to point to Neon
- Decouple DB from Railway; API stays on Railway unchanged
- Zero code changes required

**Step 2 — Migrate API to AWS Lambda** *(medium effort)*
- Add Mangum adapter (`handler = Mangum(app)`) to `apps/api/main.py`
- Package and deploy Lambda function
- Expose via Lambda Function URL (no API Gateway needed initially)
- Update `vercel.json` rewrite destination to the Function URL
- Neon's built-in connection pooler handles Lambda's stateless connections
- Update `deploy.yaml` GitHub Actions workflow (replace Railway CLI with AWS CLI)

**Step 3 — Migrate newsletter pipeline to AWS Lambda + EventBridge** *(medium effort)*
- Package `apps/newsletter_pipeline/main` as a separate Lambda function
- Create EventBridge Scheduler rule (replaces GitHub Actions cron)
- Reliable, exact-time scheduling — no more peak-hour queue delays
- Remove `newsletter.yaml` GitHub Actions workflow (or repurpose it for Lambda deploy)

**Step 4 — Custom domain with API Gateway HTTP API** *(low effort, when needed)*
- Replace Lambda Function URL with API Gateway HTTP API
- Associate `api.coado.club` as custom domain
- ~$1/million requests — negligible at current scale
- Alternative: CloudFront in front of Function URL (more complex, more features)

**Step 5 — Migrate email to AWS SES** *(medium effort)*
- Add SES provider implementing the existing `Mailer` protocol in `packages/mailer/`
- Request SES production access via AWS Support (sandbox only allows verified
  emails by default — approval typically takes 24-48h)
- Configure SPF and DKIM on `coado.club` DNS during the request
- Configure bounce/complaint handling via SNS (maps naturally to existing
  `soft_delete` logic)
- Replace Resend — cost drops from ~$20/50k emails to ~$0.10/1k emails

### Long term
- Subscriber segments
- Multi-language support
- Route 53 for DNS consolidation (migrate `coado.club` DNS into AWS)

## 🧪 Testing plan

```
tests/
├── conftest.py                          ← shared fixtures (done)
├── unit/
│   ├── models/
│   ├── schemas/
│   └── services/
│       └── test_subscription_service.py ← done
└── integration/
    ├── test_endpoints.py
    └── test_pipeline.py
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

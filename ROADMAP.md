# 🗺️ Roadmap

Where Coado is and where it's going. This tracks the real state of the project —
done, in progress, and planned.

## ✅ Done

### Signup site + API
- FastAPI app with REST endpoints (`/v1/`)
- PostgreSQL with Alembic migrations
- Email validation via Pydantic
- Deployed on AWS Lambda (SAM, Function URL, `sa-east-1`)
- Branding and visual identity (Coado design system: colors, Fraunces + Inter,
  logo, decorative elements)
- Frontend moved to Vercel with a rewrite proxy to the API (Lambda Function URL)
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
- AI provider abstraction with Anthropic implementation (`packages/ai/providers/`)
- ruff, mypy, pre-commit, Dependabot
- Technical documentation under `docs/`
- Branding refinement (tagline, visual polish)

### Testing
- Unit tests: services (`SubscriptionService`, `NewsletterService`), schemas, scraper
- Integration tests: subscribe, unsubscribe, stats endpoints
- Fakes: `FakeMailer`, `FakeAI` for isolated testing
- CI running tests on GitHub Actions

### Infrastructure
- Database migrated to Neon (PostgreSQL, free tier, built-in connection pooler)
- API migrated to AWS Lambda (`sa-east-1`) via AWS SAM (`template.yaml`), Mangum
  adapter, exposed through a Lambda Function URL
- `vercel.json` rewrite now points at the Function URL
- Remaining cleanup: `deploy.yaml` / `railway.toml` still reference Railway (to be
  removed once the SAM deploy step replaces the Railway deploy)

## 🎯 Planned

### Short term
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
Remaining ordered steps — each is independent and does not require the next to be
done first. (Database → Neon and API → AWS Lambda are done; see ✅ Done above.)

**Step 1 — Migrate newsletter pipeline to AWS Lambda + EventBridge** *(medium effort)*
- Add pipeline Lambda function to `template.yaml` (SAM)
- Create EventBridge Scheduler rule in SAM template (replaces GitHub Actions cron)
- Reliable, exact-time scheduling — no more peak-hour queue delays
- `newsletter.yaml` GitHub Actions workflow becomes the Lambda deploy step only

**Step 2 — Custom domain with API Gateway HTTP API** *(low effort, when needed)*
- Replace Lambda Function URL with API Gateway HTTP API
- Associate `api.coado.club` as custom domain
- ~$1/million requests — negligible at current scale
- Alternative: CloudFront in front of Function URL (more complex, more features)

**Step 3 — Migrate email to AWS SES** *(medium effort)*
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
- Frontend: Vercel stays as-is — free, zero ops, already decoupled via rewrite proxy.
  If full AWS consolidation becomes a goal, Amplify Hosting is the natural choice
  (replaces `vercel.json` rewrites natively; user has experience with Amplify since v1)

## 🧪 Testing

```
tests/
├── conftest.py
├── fakes/
│   ├── fake_mailer.py
│   └── fake_ai.py
├── fixtures/
│   └── sample_feed.xml
├── unit/
│   ├── test_schemas.py
│   ├── test_scraper.py
│   └── services/
│       ├── test_subscriber_service.py
│       └── test_newsletter_service.py
└── integration/
    ├── test_subscribe_endpoint.py
    ├── test_unsubscribe_endpoint.py
    └── test_stats_endpoint.py
```

## 🧭 Study direction

This project is a vehicle for consolidating Tier 1 backend skills before moving
into applied AI. Once it stabilizes, the next focus is foundational applied AI —
embeddings, RAG, streaming, vector databases — and later more advanced areas
(MCP, fine-tuning). Agentic patterns are intentionally deferred; the pipeline is
deterministic orchestration by design, not an agent.

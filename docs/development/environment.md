# Environment Variables

Configuration is managed through Pydantic Settings in `packages/core/config.py`.
Variables are loaded from a `.env` file locally and from the platform's secret
store in production (Railway for the API, GitHub Actions secrets for the
pipeline).

## Local `.env`

Copy the example and fill in your values:

```bash
cp .env.example .env
```

### Database

Nested settings use the `COFFEE_DATABASE__` prefix with a double-underscore
delimiter:

```env
COFFEE_DATABASE__HOST=localhost
COFFEE_DATABASE__PORT=5432
COFFEE_DATABASE__USER=local_user
COFFEE_DATABASE__DB=local_db
COFFEE_DATABASE__PASSWORD=local_password
```

### AI provider (Claude API)

Anthropic settings are nested under the `AI_PROVIDER` group, so they use the
double-underscore delimiter:

```env
COFFEE_AI_PROVIDER__API_KEY=sk-ant-...
# optional — defaults defined in packages/ai/schemas.py:
COFFEE_AI_PROVIDER__MODEL=claude-haiku-4-5-20251001
COFFEE_AI_PROVIDER__MAX_TOKENS=2000
```

Used by `packages/ai` for article summarization.

### Resend (email)

The sender address differs by email type, so the two are configured separately:

```env
COFFEE_RESEND_API_KEY=re_...
COFFEE_FROM_EMAIL_NEWSLETTER=newsletter@coado.club
COFFEE_FROM_EMAIL_WELCOME=welcome@coado.club
```

Used by `packages/mailer` to deliver the newsletter and welcome emails.

### Application & security

```env
COFFEE_SECRET_KEY=...               # required — signs one-click unsubscribe tokens (HMAC-SHA256)
COFFEE_ENVIRONMENT=development       # any value other than "development" enables the security headers
COFFEE_DEBUG=false
COFFEE_API_URL=https://coffee.guicardoso.dev.br
```

`ALLOWED_HOSTS` and `CORS_ORIGINS` ship with working defaults; override them with
a JSON array when needed:

```env
COFFEE_ALLOWED_HOSTS=["coffee.guicardoso.dev.br","localhost","127.0.0.1"]
COFFEE_CORS_ORIGINS=["https://coffee.guicardoso.dev.br"]
```

## Production — API (Railway)

The same `COFFEE_`-prefixed variables are set as Railway service variables. There
is no `DATABASE_URL` shortcut — the connection URI is assembled from the
individual `COFFEE_DATABASE__*` components (`packages/database/schemas.py`), so
Railway's PostgreSQL connection values go into those:

- `COFFEE_DATABASE__HOST`, `COFFEE_DATABASE__PORT`, `COFFEE_DATABASE__USER`,
  `COFFEE_DATABASE__DB`, `COFFEE_DATABASE__PASSWORD`
- `COFFEE_AI_PROVIDER__API_KEY`
- `COFFEE_RESEND_API_KEY`
- `COFFEE_FROM_EMAIL_NEWSLETTER`, `COFFEE_FROM_EMAIL_WELCOME`
- `COFFEE_SECRET_KEY`
- `COFFEE_ENVIRONMENT=production`

## Production — pipeline (GitHub Actions)

The weekly pipeline reads the same `COFFEE_`-prefixed settings, injected from the
repository's Actions secrets and variables by `.github/workflows/newsletter.yaml`
(database connection details plus the provider keys and `COFFEE_SECRET_KEY` for
unsubscribe links), separate from the Railway service.

## Notes

- Keep `.env` in `.gitignore` — never commit credentials.
- Provider-specific settings load from their own prefix, so adding a new provider
  means adding a settings block with its `env_prefix`, not threading variables
  through unrelated config.
- Configuration is validated at startup; a missing or malformed value fails fast
  rather than surfacing deep inside a request or a pipeline run.
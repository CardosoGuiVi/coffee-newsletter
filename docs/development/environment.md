# Environment Variables

Configuration is managed through Pydantic Settings in `packages/core/config.py`.
Variables are loaded from a `.env` file locally and from the platform's secret
store in production (AWS Lambda for the API, GitHub Actions secrets for the
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
COFFEE_API_URL=https://coado.club/v1    # required — API base (used to build unsubscribe links)
COFFEE_BASE_URL=https://coado.club       # required — the public site, shown in emails
```

Both `COFFEE_API_URL` and `COFFEE_BASE_URL` are **required** (no defaults). Locally
they typically point at `http://localhost:8000` and `http://localhost:8080`.

`ALLOWED_HOSTS` and `CORS_ORIGINS` ship with working defaults
(`["localhost","127.0.0.1"]`); override them with a JSON array when needed. The
API host must be listed in `ALLOWED_HOSTS` — in production that is the Lambda
Function URL host that Vercel's rewrite forwards to:

```env
COFFEE_ALLOWED_HOSTS=["coado.club","www.coado.club","<fn-id>.lambda-url.sa-east-1.on.aws","localhost","127.0.0.1"]
COFFEE_CORS_ORIGINS=["https://coado.club","https://www.coado.club"]
```

## Production — API (AWS Lambda)

The same `COFFEE_`-prefixed variables are provided to the Lambda function through
`template.yaml`: non-secret values live in `Globals.Function.Environment`, and
secrets (DB password, provider keys, app secret) are passed as SAM parameters
(`make deploy` assembles them). There is no `DATABASE_URL` shortcut — the
connection URI is assembled from the individual `COFFEE_DATABASE__*` components
(`packages/database/schemas.py`), which hold Neon's PostgreSQL connection values:

- `COFFEE_DATABASE__HOST`, `COFFEE_DATABASE__PORT`, `COFFEE_DATABASE__USER`,
  `COFFEE_DATABASE__DB`, `COFFEE_DATABASE__PASSWORD` (Neon)
- `COFFEE_AI_PROVIDER__API_KEY`
- `COFFEE_RESEND_API_KEY`
- `COFFEE_FROM_EMAIL_NEWSLETTER`, `COFFEE_FROM_EMAIL_WELCOME`
- `COFFEE_SECRET_KEY`
- `COFFEE_ENVIRONMENT=production`
- `COFFEE_API_URL=https://coado.club/v1`, `COFFEE_BASE_URL=https://coado.club`
- `COFFEE_ALLOWED_HOSTS` — includes `coado.club`, `www.coado.club`, and the
  Lambda Function URL host
- `COFFEE_CORS_ORIGINS` — `https://coado.club`, `https://www.coado.club`

## Production — pipeline (AWS Lambda)

The weekly pipeline runs as its own Lambda function (`coado-newsletter`,
triggered by EventBridge Scheduler) and reads the exact same `Globals` block in
`template.yaml` as the API function — same Neon connection, provider keys, and
`COFFEE_SECRET_KEY` for signing unsubscribe tokens. There is no separate config
surface for the pipeline.

## Notes

- Keep `.env` in `.gitignore` — never commit credentials.
- Provider-specific settings load from their own prefix, so adding a new provider
  means adding a settings block with its `env_prefix`, not threading variables
  through unrelated config.
- Configuration is validated at startup; a missing or malformed value fails fast
  rather than surfacing deep inside a request or a pipeline run.
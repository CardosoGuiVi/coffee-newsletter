# Deployment

Coado is deployed across three platforms, each handling what it does best:

| Component | Platform        | Trigger                                  |
|-----------|-----------------|------------------------------------------|
| API       | Railway         | Deploy on merge to `main`                |
| Frontend  | Vercel          | `main` → production, other branches → preview |
| Pipeline  | GitHub Actions  | Scheduled cron (Mondays 11:00 UTC)       |

## API — Railway

The FastAPI service runs on Railway with a single replica, which suits the
traffic profile (see [decisions](../architecture/decisions.md)). Migrations run
as a pre-deploy step, before the new release starts taking traffic.

Deploy configuration (`railway.toml`):

```toml
[deploy]
preDeployCommand = "alembic upgrade head"
startCommand = "uv run fastapi run --port $PORT"
healthcheckPath = "/v1/health"
```

Deployment is driven by a GitHub Actions workflow that runs `railway up` via the
Railway CLI on merge to `main`, using a `RAILWAY_TOKEN` secret. Because the deploy
is CLI-driven, the Railway service does not need its native GitHub integration
connected — keeping a single source of truth for what triggers a deploy.

Required environment variables are listed in [environment.md](../development/environment.md).

## Frontend — Vercel

The static frontend lives in `apps/web` and is hosted on Vercel.

- **Production branch:** `main` → serves `coado.club`.
- **Preview:** every non-production branch gets an automatic preview URL.

The domain `coado.club` is managed through Vercel's nameservers, with Vercel
issuing SSL automatically.

The two surfaces live on separate domains: `coado.club` is the public frontend
(Vercel), and `coffee.guicardoso.dev.br` is the Railway API host. The API domain
is not user-facing — the browser only ever sees `coado.club`, and the rewrite
proxy below forwards `/v1/*` to the API behind the scenes.

### Routing and the API proxy

`apps/web` is a small multi-page static site. `vercel.json` configures the
routing:

```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    { "source": "/v1/(.*)", "destination": "https://coffee.guicardoso.dev.br/v1/$1" }
  ]
}
```

- **API proxy** — `/v1/*` is rewritten to the Railway API, so the browser only
  ever talks to the Vercel origin (no CORS) and the frontend's `fetch` calls stay
  relative.
- **Clean URLs** — with `cleanUrls`, each page is served from its `.html` file
  without the extension: `/` (`index.html`), `/privacy`, `/terms`, `/unsubscribe`.
- **Errors** — unmatched paths fall back to Vercel's static `404.html`; `500.html`
  covers server failures.

There is intentionally **no** SPA catch-all rewrite to `/index.html` — that would
swallow the other pages and prevent a real 404. See the
[frontend pages](../development/getting-started.md#pages-and-routes) for the full
route list.

> **Preview note:** preview deployments proxy to the *same* production Railway
> API (there is a single API environment). Be mindful when testing the signup
> form from a preview URL, since it writes to the real database.

## Pipeline — GitHub Actions

The newsletter pipeline is a scheduled workflow, not a long-running service. It
runs every Monday at 11:00 UTC, executing `apps/newsletter_pipeline`. Provider
credentials come from repository Actions secrets. See
[pipeline.md](pipeline.md) for the run flow.

## CI

Beyond the scheduled job, GitHub Actions also handles continuous integration
(linting, type checks) and release automation. Dependabot keeps dependencies
current.
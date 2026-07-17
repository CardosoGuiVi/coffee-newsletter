# Deployment

Coado is deployed across three platforms, each handling what it does best:

| Component | Platform        | Trigger                                  |
|-----------|-----------------|------------------------------------------|
| API       | AWS Lambda (`sa-east-1`) | SAM — `make deploy`             |
| Frontend  | Vercel          | `main` → production, other branches → preview |
| Pipeline  | AWS Lambda (`sa-east-1`) | EventBridge Scheduler (Mondays 11:00 UTC) |

## API — AWS Lambda

The FastAPI app runs as a single AWS Lambda function (`coado-api`) in `sa-east-1`,
fronted by a **Lambda Function URL**. The Mangum adapter
(`handler = Mangum(app, lifespan="off")` in `apps/api/main.py`) bridges Lambda's
event model to ASGI. This suits the traffic profile — no idle compute between
requests (see [decisions](../architecture/decisions.md)).

Infrastructure is defined with **AWS SAM** in `template.yaml`:

- **Function** `coado-api` — handler `apps.api.main.handler`, python3.12, 256 MB,
  30 s timeout.
- **Layer** `coado-dependencies` — third-party dependencies, rebuilt with
  `make build-layer` only when dependencies change.
- **Function URL** — `AuthType: NONE` with a CORS allowlist (`coado.club` and the
  Vercel preview host); methods `GET`/`POST`.
- Non-secret config (Neon host, base URLs, allowed hosts) is baked into the
  template's `Globals.Function.Environment`; secrets (DB password, Anthropic and
  Resend keys, app secret) are passed as SAM parameters.

Deploy from a local checkout:

```bash
make deploy   # make_sam_params.sh → build-function → sam build && sam deploy
```

`make deploy` assembles the secret parameters, copies `apps/` + `packages/` into
`.build/function/`, then runs `sam build && sam deploy`. Database migrations are
**not** part of the deploy — run them separately against Neon with
`make db-migrate` (`alembic upgrade head`) when a release includes schema changes.

> **Note:** deploys are run manually via `make deploy` from a local checkout —
> there is no automated GitHub Actions deploy yet. Wiring up a SAM deploy step
> (with AWS credentials in Actions secrets) is a planned follow-up.

Required environment variables are listed in [environment.md](../development/environment.md).

## Frontend — Vercel

The static frontend lives in `apps/web` and is hosted on Vercel.

- **Production branch:** `main` → serves `coado.club`.
- **Preview:** every non-production branch gets an automatic preview URL.

The domain `coado.club` is managed through Vercel's nameservers, with Vercel
issuing SSL automatically.

The browser only ever talks to `coado.club` (Vercel). The API has no public
domain of its own yet — it is served straight from the raw Lambda Function URL,
and the rewrite proxy below forwards `/v1/*` to it behind the scenes. (A custom
`api.coado.club` via API Gateway is a planned step — see [ROADMAP](../../ROADMAP.md).)

### Routing and the API proxy

`apps/web` is a small multi-page static site. `vercel.json` configures the
routing:

```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    { "source": "/v1/(.*)", "destination": "https://rwkpejfc3ynbif3u6dhsdhg2we0vpapa.lambda-url.sa-east-1.on.aws/v1/$1" }
  ]
}
```

- **API proxy** — `/v1/*` is rewritten to the Lambda Function URL, so the browser
  only ever talks to the Vercel origin (no CORS) and the frontend's `fetch` calls
  stay relative.
- **Clean URLs** — with `cleanUrls`, each page is served from its `.html` file
  without the extension: `/` (`index.html`), `/about`, `/privacy`, `/terms`,
  `/unsubscribe`.
- **Errors** — unmatched paths fall back to Vercel's static `404.html`; `500.html`
  covers server failures.

There is intentionally **no** SPA catch-all rewrite to `/index.html` — that would
swallow the other pages and prevent a real 404. See the
[frontend pages](../development/getting-started.md#pages-and-routes) for the full
route list.

> **Preview note:** preview deployments proxy to the *same* production Lambda
> API (there is a single API environment). Be mindful when testing the signup
> form from a preview URL, since it writes to the real database.

## Pipeline — AWS Lambda + EventBridge Scheduler

The newsletter pipeline runs as its own Lambda function (`coado-newsletter`),
sharing the same SAM template, dependency layer, and config as the API
function — only the handler differs (`apps.newsletter_pipeline.main.handler`).
It is not fronted by a Function URL; the only trigger is an EventBridge
Scheduler event source defined on the function in `template.yaml`, firing every
Monday at 11:00 UTC. Because it runs for minutes rather than milliseconds, its
`Timeout` (900s) and `MemorySize` (1024 MB) are overridden above the `Globals`
defaults used by the API function.

See [pipeline.md](pipeline.md) for the run flow, retry behavior, and how to
invoke it manually for verification.

## CI

Beyond the scheduled job, GitHub Actions also handles continuous integration.
On every push and pull request to `main` and `development`, the CI workflow
(`.github/workflows/ci.yml`) spins up a PostgreSQL service container and runs the
full test suite with coverage:

```bash
uv run pytest --cov=packages --cov=apps --cov-report=xml --cov-report=term-missing -q
```

Coverage is uploaded to Codecov and posted as a comment on pull requests
(`MishaKav/pytest-coverage-comment`). Linting and type checks (ruff, mypy) run via
pre-commit, release automation handles versioning, and Dependabot keeps
dependencies current.
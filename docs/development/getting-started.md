# Getting Started

How to run Coado locally. The frontend and API run separately, mirroring
production (Vercel for the frontend, Railway for the API).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker (for running PostgreSQL locally)
- [Make](https://www.gnu.org/software/make/) for the shortcut commands

## 1. Clone and install

```bash
git clone git@github.com:CardosoGuiVi/coffee-newsletter.git
cd coffee-newsletter
uv sync
```

## 2. Configure environment

```bash
cp .env.example .env
# edit .env with your credentials
```

See [environment.md](environment.md) for the full list of variables and what
each one does.

## 3. Run the API

**With Docker (recommended):**

```bash
make fastapi-dev
```

This brings up PostgreSQL via Docker, runs Alembic migrations, and starts FastAPI
at `http://localhost:8000`.

**Without Docker** (requires an external PostgreSQL):

```bash
uv run --env-file .env fastapi dev
```

The API routes are served under the `/v1/` prefix (for example
`http://localhost:8000/v1/stats`).

## 4. Run the frontend

The frontend is static (vanilla HTML/CSS/JS) and is no longer served by FastAPI.
Serve it with any static server:

```bash
cd apps/web
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

### Pages and routes

The frontend is a multi-page static site:

| Route          | File                    | Notes                                            |
|----------------|-------------------------|--------------------------------------------------|
| `/`            | `index.html`            | Signup form + live stats                         |
| `/about`       | `about.html`            | About the project, stack, and author links       |
| `/unsubscribe` | `unsubscribe.html`      | Calls `POST /v1/unsubscribe`; accepts `?email=`  |
| `/privacy`     | `privacy.html`          | Privacy policy                                    |
| `/terms`       | `terms.html`            | Terms of service                                 |
| 404 / 500      | `404.html` / `500.html` | Error pages                                       |

On Vercel these resolve as clean URLs (`/privacy`, `/unsubscribe`, …).
`python3 -m http.server` does **not** emulate Vercel's `cleanUrls`, so locally
either open the `.html` files directly (e.g. `/privacy.html`) or run
`npx vercel dev` for production-accurate routing (clean URLs, `404.html`
fallback, and the `/v1` proxy).

> Testing `/unsubscribe` end-to-end needs the API running and an existing
> subscriber. Because the page is served cross-origin from the local API, add the
> static origin to `COFFEE_CORS_ORIGINS` (e.g. `["http://localhost:8080"]`) in
> your `.env`.

### Pointing the frontend at the local API

In production, a Vercel rewrite proxies `/v1/*` to the Railway API, so the
frontend's `fetch` calls are relative. Locally there is no such proxy, so point
the frontend at the local API with a small config file.

Create `apps/web/js/config.js`:

```js
window.API_BASE = 'http://localhost:8000';
```

Load it before the main script in `index.html`:

```html
<script src="/js/config.js"></script>
<script src="/js/index.js"></script>
```

And read it in the fetch calls, falling back to a relative path in production:

```js
const res = await fetch(`${window.API_BASE ?? ''}/v1/stats`);
```

Add `config.js` to `.gitignore` so the local URL is never committed:

```
apps/web/js/config.js
```

In production `config.js` does not exist, `API_BASE` is `undefined`, and the
fetches stay relative — letting the Vercel rewrite do its job.

## Database migrations

```bash
# create a new migration after model changes
uv run alembic revision --autogenerate -m "description of change"

# apply migrations
uv run alembic upgrade head

# check current revision
uv run alembic current
```

## Running the pipeline manually

```bash
uv run --env-file .env python apps/newsletter_pipeline/main.py
```

## Useful commands

```bash
uv sync                  # install dependencies
make fastapi-dev         # run API with hot reload (Docker DB)
make db-up               # start the database only
make db-down             # stop the database
uv run ruff check .      # lint
uv run ruff format .     # format
uv run mypy .            # type check
```
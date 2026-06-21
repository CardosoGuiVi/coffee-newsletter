# Architecture Decisions

This document records the reasoning behind the project's key technical choices.
Each entry captures the context, the decision, and the trade-offs — so a future
reader (or a future me) understands *why*, not just *what*.

## Deterministic orchestration, not an agent

**Decision:** The pipeline is plain orchestrated code, not an agent.

The newsletter pipeline runs a fixed sequence: scrape RSS → summarize each
article with the Claude API → render the email → send via Resend. There is no
tool use, no feedback loop, and no autonomous iteration. The LLM is used purely
as a summarization step within a deterministic flow.

**Why:** Two reasons. First, cost — agentic loops consume far more tokens, and
for a weekly personal newsletter that overhead buys nothing. Second, honesty
about what the system is: calling this an "AI agent" would be inaccurate. It is
deterministic code that happens to call an LLM. Framing it correctly keeps the
architecture and the learning goals clear.

**Trade-off:** No adaptive behavior. If a feed changes shape or an article
resists summarization, the pipeline does not "reason around" it. That is an
acceptable limitation for the use case, and revisiting agentic patterns is a
deliberate future step, not an oversight.

## Frontend and API on separate hosts

**Decision:** The static frontend is hosted on Vercel; the API runs on Railway.
They are wired together with a Vercel rewrite proxy.

The browser only ever talks to the Vercel domain (`coado.club`). Requests to
`/v1/*` are rewritten by Vercel to the Railway API host
(`coffee.guicardoso.dev.br`) behind the scenes:

```json
{
  "rewrites": [
    { "source": "/v1/(.*)", "destination": "https://coffee.guicardoso.dev.br/v1/$1" }
  ]
}
```

**Why:** This keeps everything under one origin from the browser's perspective,
so normal frontend traffic never triggers a cross-origin request or a preflight.
The frontend's `fetch` calls stay relative (`/v1/stats`), so the same code works
in preview and production. Vercel also gives the static site a global CDN and
automatic SSL for free. The API still configures `CORSMiddleware`
(`apps/api/main.py`) as an explicit allowlist for any direct cross-origin
access, rather than relying on the proxy alone.

**Trade-off:** Two deploy targets to manage instead of one. Previously the
FastAPI app served the frontend via `StaticFiles`; that was removed once the
frontend moved to Vercel.

## Scheduled cron, not a long-running worker

**Decision:** The newsletter pipeline runs as a scheduled GitHub Actions job
(Mondays at 11:00 UTC), not as a persistent service.

**Why:** The workload is intermittent — it runs once a week for a few minutes.
A long-running worker would sit idle 99.9% of the time while still consuming
resources. GitHub Actions cron is free for this cadence, versioned alongside the
code, and requires no extra infrastructure.

**Trade-off:** Cold start each run and a hard dependency on GitHub Actions
availability/scheduling precision (cron can drift by a few minutes). Neither
matters for a weekly email.

## Single API replica on Railway

**Decision:** The API runs with a single replica on Railway.

**Why:** The traffic profile is a low-volume signup form plus occasional stats
reads. One replica handles this comfortably, and avoiding horizontal scaling
keeps things simple and cheap.

**Trade-off:** This constrains in-memory state. Notably, `slowapi` rate limiting
stores counters in process memory, which only works correctly with a single
replica. Scaling beyond one would require a shared backend (Redis). This is a
known boundary, documented so the limitation is intentional rather than a
surprise.

## Pydantic Settings for configuration

**Decision:** All configuration lives in `packages/core/config.py` using Pydantic
Settings, with provider-specific settings grouped behind a provider abstraction.

**Why:** Centralizing config avoids duplication across the API and the pipeline,
gives type-safe settings, and lets each provider's settings load from its own
`env_prefix` (e.g. `ANTHROPIC_*`). Configuration is validated at startup rather
than failing deep inside a request.

**Trade-off:** Nested `BaseSettings` classes lose their own env-loading behavior
when embedded in a parent, so provider settings are instantiated independently
to keep coupling low. This is a deliberate choice favoring independence over deep
nesting.

## Cost-conscious defaults

A recurring principle across decisions: prefer the pragmatic option until real
data justifies more complexity. Examples include using `claude-haiku` for
summarization (cheaper, sufficient for the task), not setting Railway resource
maximums before observing actual usage, and deferring features like JWT-based
unsubscribe tokens until they are actually needed.
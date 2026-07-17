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

**Decision:** The static frontend is hosted on Vercel; the API runs on AWS Lambda
(Function URL). They are wired together with a Vercel rewrite proxy.

The browser only ever talks to the Vercel domain (`coado.club`). Requests to
`/v1/*` are rewritten by Vercel to the Lambda Function URL behind the scenes:

```json
{
  "rewrites": [
    { "source": "/v1/(.*)", "destination": "https://<fn-id>.lambda-url.sa-east-1.on.aws/v1/$1" }
  ]
}
```

The Function URL host must be listed in the API's `ALLOWED_HOSTS`
(`TrustedHostMiddleware`) or requests are rejected with `400`; `template.yaml`
sets it alongside `coado.club`. A custom `api.coado.club` via API Gateway is a
planned step — today the rewrite targets the raw Function URL.

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

## Scheduled Lambda, not a long-running worker

**Decision:** The newsletter pipeline runs as its own AWS Lambda function
(`coado-newsletter`), triggered weekly by an EventBridge Scheduler schedule
(Mondays at 11:00 UTC), not as a persistent service.

**Why:** The workload is intermittent — it runs once a week for a few minutes.
A long-running worker would sit idle 99.9% of the time while still consuming
resources. This started as a GitHub Actions cron job; it moved to Lambda +
EventBridge Scheduler once the API had already migrated to Lambda, so the
pipeline could share the same SAM template, dependency layer, and config
instead of maintaining a second deploy path. EventBridge Scheduler also fires
at the exact configured time — GitHub Actions' shared cron matrix queues jobs
at busy times (e.g. `:00`), which is why the schedule had briefly moved to an
off-peak minute (`07:17`); that workaround is no longer needed and the schedule
reverted to a round `11:00 UTC`.

**Trade-off:** Cold start each run. The 15-minute Lambda timeout is a hard
ceiling the old GitHub Actions job (6-hour default) didn't have — irrelevant
today, but a real constraint if the subscriber list or send loop grows enough
to approach it (see [pipeline.md](../infrastructure/pipeline.md)).

## In-process rate limiting and horizontal scale

**Decision:** Rate limiting uses `slowapi` with in-process counters, accepting
that the deployment behaves as effectively one instance.

**Why:** The traffic profile is a low-volume signup form plus occasional stats
reads. In-memory counters avoid an extra dependency (Redis) and are plenty for
this volume.

**Trade-off:** In-process counters assume a single instance. On Railway this held
via one replica; on AWS Lambda each concurrent execution environment keeps its
own counters, so under concurrency the effective limit is per-instance
(best-effort) rather than global. At current volume Lambda usually serves from a
single warm instance, but strict global limits would need a shared backend
(Redis / DynamoDB). This is a known boundary, documented intentionally.

## Pydantic Settings for configuration

**Decision:** All configuration lives in `packages/core/config.py` using Pydantic
Settings, with provider-specific settings grouped behind a provider abstraction.

**Why:** Centralizing config avoids duplication across the API and the pipeline
and gives type-safe settings. Provider-specific settings are grouped into nested
models (e.g. `AI_PROVIDER`, `DATABASE`) and loaded via the `COFFEE_` prefix with a
`__` nested delimiter — so `COFFEE_AI_PROVIDER__API_KEY` and
`COFFEE_DATABASE__HOST` map onto the right group. Configuration is validated at
startup rather than failing deep inside a request.

**Trade-off:** Nested models are plain `BaseModel`s populated through the parent's
nested delimiter, not independent `BaseSettings` with their own `.env` loading.
This keeps a single source of truth at the cost of every variable carrying the
`COFFEE_` prefix.

## Cost-conscious defaults

A recurring principle across decisions: prefer the pragmatic option until real
data justifies more complexity. Examples include using `claude-haiku-4-5` for
summarization (cheaper, sufficient for the task), keeping the Lambda modestly
sized (256 MB) rather than over-provisioning before observing actual usage, and
deferring features like JWT-based unsubscribe tokens until they are actually
needed.
# Newsletter Pipeline

The pipeline builds and sends the weekly newsletter. It is deterministic
orchestrated code — a fixed sequence of steps, with no agentic behavior (see
[decisions](../architecture/decisions.md)).

## Schedule

Runs every **Monday at 11:00 UTC** (08:00 BRT) via an **EventBridge Scheduler**
schedule (`cron(0 11 ? * MON *)`), defined in `template.yaml` as an event source
on the `coado-newsletter` Lambda function. The entrypoint is
`apps/newsletter_pipeline/main.py`, which wires together the packages and
executes the flow.

EventBridge Scheduler fires at the exact configured time — unlike GitHub
Actions' shared cron matrix (which the pipeline used before this migration),
there is no queueing delay to work around.

## Flow

```
EventBridge Scheduler (Monday 11:00 UTC)
  ↓
Lambda: coado-newsletter → apps/newsletter_pipeline
  ├── packages/scraper     → collect RSS feeds (Brazilian + international sources)
  ├── packages/ai          → summarize each article with the Claude API (claude-haiku-4-5)
  ├── packages/newsletter  → render the email with Jinja2 templates
  └── packages/mailer      → send to all subscribers via Resend
```

Each step is owned by a single package:

1. **Scrape** — `packages/scraper` fetches and parses the configured RSS feeds
   using `feedparser`, producing a normalized list of articles.
2. **Summarize** — `packages/ai` sends each article to the Claude API and gets
   back a concise summary. `claude-haiku-4-5` is used for cost efficiency.
3. **Render** — `packages/newsletter` composes the summaries into the email body
   using Jinja2 templates (`newsletter.html`, `newsletter_item.html`).
4. **Send** — `packages/mailer` delivers the rendered email to every active
   subscriber through Resend.

## Why a scheduled function and not a worker

The job runs for a few minutes once a week. A persistent worker would idle the
rest of the time for no benefit. A scheduled Lambda invocation needs no extra
infrastructure and costs nothing between runs. Cold start is irrelevant for a
weekly email.

## Retries and duplicate sends

The schedule sets `RetryPolicy.MaximumRetryAttempts: 0`. The send loop in
`CampaignService.send_newsletter` is **not idempotent** — it is a plain
sequential loop over active subscribers, so a retry after a partial failure
would re-send to everyone already emailed in the failed attempt. Disabling
retries is the cheapest way to avoid duplicate sends today; a failed run must be
re-triggered manually (see below) after checking how far it got via CloudWatch
Logs.

Isolating delivery behind SQS (per-recipient retries and a DLQ, instead of an
all-or-nothing retry) is planned — see [ROADMAP](../../ROADMAP.md).

## Email rendering notes

Templates live in `packages/newsletter/templates/`, close to the domain
rather than in a global folder. A few hard-won rendering constraints:

- Gmail strips `<style>` blocks, so defaults must be set with inline `style=""`
  attributes.
- `@media (prefers-color-scheme: dark)` handles dark mode on Gmail iOS.
- Layouts are table-based for client compatibility.

## Running manually

**Locally**, for testing or a one-off send:

```bash
uv run --env-file .env python apps/newsletter_pipeline/main.py
```

This uses the same credentials as production, so it will send real email if
pointed at a live Resend key — use a test configuration when experimenting.

**Against the deployed Lambda**, invoke it directly. The `handler` reads two
optional keys from the invocation payload, both meant for verifying a deploy
without emailing every subscriber:

```bash
# build the newsletter and log the subject/recipient count, send nothing
aws lambda invoke --function-name coado-newsletter \
  --payload '{"dry_run": true}' --cli-binary-format raw-in-base64-out out.json

# full send, but only to one address
aws lambda invoke --function-name coado-newsletter \
  --payload '{"test_email": "you@example.com"}' --cli-binary-format raw-in-base64-out out.json

# real weekly run — same payload EventBridge sends ({})
aws lambda invoke --function-name coado-newsletter \
  --payload '{}' --cli-binary-format raw-in-base64-out out.json
```
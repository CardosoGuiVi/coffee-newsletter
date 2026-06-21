# Newsletter Pipeline

The pipeline builds and sends the weekly newsletter. It is deterministic
orchestrated code — a fixed sequence of steps, with no agentic behavior (see
[decisions](../architecture/decisions.md)).

## Schedule

Runs every **Monday at 11:00 UTC** via GitHub Actions cron. The entrypoint is
`apps/newsletter_pipeline`, which wires together the packages and executes the
flow.

## Flow

```
GitHub Actions cron (Monday 11:00 UTC)
  ↓
apps/newsletter_pipeline
  ├── packages/scraper     → collect RSS feeds (Brazilian + international sources)
  ├── packages/ai          → summarize each article with the Claude API (claude-haiku)
  ├── packages/newsletter  → render the email with Jinja2 templates
  └── packages/mailer      → send to all subscribers via Resend
```

Each step is owned by a single package:

1. **Scrape** — `packages/scraper` fetches and parses the configured RSS feeds
   using `feedparser`, producing a normalized list of articles.
2. **Summarize** — `packages/ai` sends each article to the Claude API and gets
   back a concise summary. `claude-haiku` is used for cost efficiency.
3. **Render** — `packages/newsletter` composes the summaries into the email body
   using Jinja2 templates (`newsletter.html`, `newsletter_item.html`).
4. **Send** — `packages/mailer` delivers the rendered email to every active
   subscriber through Resend.

## Why a cron and not a worker

The job runs for a few minutes once a week. A persistent worker would idle the
rest of the time for no benefit. GitHub Actions cron is free at this cadence,
lives alongside the code, and needs no extra infrastructure. The trade-offs
(cold start, minor cron drift) are irrelevant for a weekly email.

## Email rendering notes

Templates live in `packages/newsletter/templates/`, close to the domain
rather than in a global folder. A few hard-won rendering constraints:

- Gmail strips `<style>` blocks, so defaults must be set with inline `style=""`
  attributes.
- `@media (prefers-color-scheme: dark)` handles dark mode on Gmail iOS.
- Layouts are table-based for client compatibility.

## Running manually

For testing or a one-off send:

```bash
uv run --env-file .env python apps/newsletter_pipeline/main.py
```

This uses the same credentials as production, so it will send real email if
pointed at a live Resend key — use a test configuration when experimenting.
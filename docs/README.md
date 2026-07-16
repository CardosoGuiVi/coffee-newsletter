# Coado — Documentation

Technical documentation for Coado, an automated weekly newsletter about coffee
(PT-BR), live at [coado.club](https://coado.club).

This directory documents the architecture, development setup, and infrastructure
behind the project. For a high-level overview, start with the
[architecture overview](architecture/overview.md).

## Index

### Architecture
- [Overview](architecture/overview.md) — the modular monolith, monorepo layout,
  and how the pieces fit together.
- [Decisions](architecture/decisions.md) — the reasoning behind key choices
  (why AWS Lambda, why no agent frameworks, why a cron over a long-running worker).
- [Packages](architecture/packages.md) — responsibility of each package under
  `packages/`.

### Development
- [Getting started](development/getting-started.md) — run the project locally.
- [Environment](development/environment.md) — required environment variables.

### API
- [Endpoints](api/endpoints.md) — the REST routes under `/v1` (subscribe,
  unsubscribe, stats, health).

### Infrastructure
- [Deployment](infrastructure/deployment.md) — AWS Lambda, Vercel, and GitHub Actions.
- [Pipeline](infrastructure/pipeline.md) — how the weekly newsletter is built and sent.

## Project at a glance

Coado has two runtime surfaces:

1. A **signup site + API** — a static frontend (hosted on Vercel) talking to a
   FastAPI service (hosted on AWS Lambda) that manages subscriptions and exposes
   public stats.
2. An **automated pipeline** — a scheduled GitHub Actions job that scrapes RSS
   feeds, summarizes articles with the Claude API, renders an email, and sends
   it via Resend.

The codebase is a monorepo: `apps/` holds thin entrypoints, `packages/` holds
all reusable domain and infrastructure logic.
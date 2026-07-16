# API Endpoints

The FastAPI service exposes a small REST API for managing subscriptions and
reading public stats. All routes are served under the `/v1` prefix
(`apps/api/routes/v1/`).

**Base URL**

| Context    | Base                                         |
|------------|----------------------------------------------|
| Production | `https://coado.club/v1` (proxied to the API) |
| API host   | `https://api.coado.club/v1`                  |
| Local      | `http://localhost:8000/v1`                   |

Rate limits are applied per client IP (`slowapi`, keyed on the remote address).
Invalid request bodies return `422 Unprocessable Entity` with Pydantic's
validation detail; email fields are validated as `EmailStr`.

---

## `POST /v1/subscribe`

Registers a new email and sends the welcome email. Rate limit: **5/minute**.

**Request**

```json
{ "email": "person@example.com" }
```

**Response — `201 Created`**

```json
{ "email": "person@example.com", "created_at": "2026-06-19T11:00:00Z" }
```

**Errors**

| Status | Condition                  | Detail                                                       |
|--------|----------------------------|--------------------------------------------------------------|
| `409`  | `EmailAlreadySubscribed`   | `Email already exists.`                                      |
| `429`  | `SubscriptionCooldownError`| `You must wait 48 hours after unsubscribing.`               |
| `502`  | `MailerError`              | `Subscribed successfully but failed to send welcome email.` |

The 48-hour cooldown blocks re-subscribing within 48 hours of unsubscribing.

---

## `POST /v1/unsubscribe`

Unsubscribes an email. Rate limit: **5/minute**.

**Request**

```json
{ "email": "person@example.com" }
```

**Response — `200 OK`**

```json
{ "message": "Unsubscribed successfully." }
```

**Errors**

| Status | Condition           | Detail            |
|--------|---------------------|-------------------|
| `404`  | `SubscriberNotFound`| `Email not found.`|

This is the endpoint behind the `/unsubscribe` web page (`apps/web/unsubscribe.html`),
which also prefills the field from an `?email=` query parameter.

---

## `POST /v1/unsubscribe/one-click`

Token-authenticated unsubscribe used by the one-click links in newsletter
emails. The `token` is an HMAC-SHA256 signature of the email
(`packages/core/tokens.py`, signed with `SECRET_KEY`). Rate limit: **5/minute**.

**Query parameters**

| Name    | Description                          |
|---------|--------------------------------------|
| `email` | The subscriber's email               |
| `token` | The unsubscribe token for that email |

```
POST /v1/unsubscribe/one-click?email=person@example.com&token=<hmac>
```

**Response — `200 OK`**

```json
{ "message": "Unsubscribed successfully." }
```

**Errors**

| Status | Condition           | Detail                      |
|--------|---------------------|-----------------------------|
| `403`  | Invalid token       | `Invalid unsubscribe token.`|
| `404`  | `SubscriberNotFound`| `Email not found.`          |

---

## `GET /v1/stats`

Public subscriber statistics. Rate limit: **30/minute**.

**Response — `200 OK`**

```json
{ "total_subscribers": 128, "joined_this_week": 9 }
```

---

## `GET /v1/health`

Liveness endpoint for uptime and monitoring checks. No rate limit.

**Response — `200 OK`**

```json
{ "status": "healthy" }
```

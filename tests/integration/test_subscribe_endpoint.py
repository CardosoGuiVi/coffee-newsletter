"""Integration tests for POST /v1/subscribe.

These tests exercise the full HTTP stack: FastAPI routing, middleware, request
validation, exception-to-HTTP mapping, and response serialisation. The DB and
mailer are replaced via dependency overrides (see conftest.py), so tests are
fast and self-contained.
"""

from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models import Subscriber
from tests.fakes.fake_mailer import FakeMailer


class TestSubscribeHappyPath:
    async def test_returns_201_with_email_and_timestamp(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post("/v1/subscribe", json={"email": "new@example.com"})

        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "new@example.com"
        assert "created_at" in body

    async def test_sends_welcome_email(
        self, client: AsyncClient, fake_mailer: FakeMailer
    ) -> None:
        """The client fixture and this test share the same FakeMailer instance,
        so we can assert on the mailer state after the HTTP call."""
        await client.post("/v1/subscribe", json={"email": "welcome@example.com"})

        assert "welcome@example.com" in fake_mailer.sent_welcomes


class TestSubscribeValidation:
    async def test_422_on_invalid_email(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/subscribe", json={"email": "not-an-email"})

        assert resp.status_code == 422

    async def test_422_on_missing_email_field(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/subscribe", json={})

        assert resp.status_code == 422


class TestSubscribeDomainErrors:
    async def test_409_if_already_subscribed(self, client: AsyncClient) -> None:
        await client.post("/v1/subscribe", json={"email": "dup@example.com"})

        resp = await client.post("/v1/subscribe", json={"email": "dup@example.com"})

        assert resp.status_code == 409
        assert resp.json()["detail"] == "Email already exists."

    async def test_429_if_within_cooldown(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Insert a recently-unsubscribed subscriber directly, bypassing the
        service, then try to re-subscribe. The client fixture uses the same
        db_session, so the inserted row is visible inside the request handler.
        """
        sub = Subscriber(
            email="cooldown@example.com",
            subscribed=False,
            unsubscribed_at=datetime.now(UTC),
        )
        db_session.add(sub)
        await db_session.flush()

        resp = await client.post(
            "/v1/subscribe", json={"email": "cooldown@example.com"}
        )

        assert resp.status_code == 429
        assert "48 hours" in resp.json()["detail"]

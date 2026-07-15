"""Integration tests for POST /v1/unsubscribe."""

from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models import Subscriber


class TestUnsubscribeHappyPath:
    async def test_returns_200_with_message(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Seed directly — don't call POST /subscribe to set up state for a
        # different endpoint. Tests should have one Act step (the HTTP call
        # under test), not two (one to arrange, one to act).
        db_session.add(Subscriber(email="leave@example.com", subscribed=True))
        await db_session.flush()

        resp = await client.post("/v1/unsubscribe", json={"email": "leave@example.com"})

        assert resp.status_code == 200
        assert resp.json()["message"] == "Unsubscribed successfully."

    async def test_marks_subscriber_as_inactive(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        from packages.newsletter.repository import SubscriberRepository

        db_session.add(Subscriber(email="soft@example.com", subscribed=True))
        await db_session.flush()

        await client.post("/v1/unsubscribe", json={"email": "soft@example.com"})

        repo = SubscriberRepository(db_session)
        sub = await repo.get_by_email("soft@example.com")
        assert sub is not None
        assert sub.subscribed is False
        assert sub.unsubscribed_at is not None

    async def test_already_unsubscribed_returns_200_without_resetting_cooldown(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Unsubscribing an already-inactive subscriber returns 200 without
        restarting the re-subscribe cooldown.

        The endpoint must never expose whether an email is subscribed, so it
        still answers 200. But unregister is a no-op when already unsubscribed:
        re-running soft_delete would reset unsubscribed_at and restart the
        30-day cooldown clock.
        """
        from packages.newsletter.repository import SubscriberRepository

        original = datetime(2026, 1, 1, tzinfo=UTC)
        db_session.add(
            Subscriber(
                email="already@example.com",
                subscribed=False,
                unsubscribed_at=original,
            )
        )
        await db_session.flush()

        resp = await client.post(
            "/v1/unsubscribe", json={"email": "already@example.com"}
        )

        assert resp.status_code == 200
        repo = SubscriberRepository(db_session)
        sub = await repo.get_by_email("already@example.com")
        assert sub is not None
        assert sub.unsubscribed_at == original  # cooldown clock left untouched


class TestUnsubscribeErrors:
    async def test_404_for_unknown_email(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/unsubscribe", json={"email": "ghost@example.com"})

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Email not found."

    async def test_422_on_invalid_email(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/unsubscribe", json={"email": "not-an-email"})

        assert resp.status_code == 422

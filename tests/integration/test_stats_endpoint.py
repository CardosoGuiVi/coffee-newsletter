"""Integration tests for GET /v1/stats."""

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models import Subscriber


class TestStatsEndpoint:
    async def test_returns_correct_shape(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/stats")

        assert resp.status_code == 200
        body = resp.json()
        assert "total_subscribers" in body
        assert "joined_this_week" in body

    async def test_counts_only_active_subscribers(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        now = datetime.now(UTC)

        db_session.add(
            Subscriber(email="active1@example.com", subscribed=True, created_at=now)
        )
        db_session.add(
            Subscriber(email="active2@example.com", subscribed=True, created_at=now)
        )
        db_session.add(
            Subscriber(email="inactive@example.com", subscribed=False, created_at=now)
        )
        await db_session.flush()

        resp = await client.get("/v1/stats")

        assert resp.json()["total_subscribers"] == 2

    async def test_joined_this_week_excludes_old_subscribers(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        now = datetime.now(UTC)
        old = now - timedelta(days=10)

        db_session.add(
            Subscriber(email="new@example.com", subscribed=True, created_at=now)
        )
        db_session.add(
            Subscriber(email="old@example.com", subscribed=True, created_at=old)
        )
        await db_session.flush()

        resp = await client.get("/v1/stats")
        body = resp.json()

        assert body["total_subscribers"] == 2
        assert body["joined_this_week"] == 1

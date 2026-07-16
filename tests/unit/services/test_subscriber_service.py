"""Unit tests for SubscriptionService.

"Unit" here means: service + real repository + test DB (via rolled-back transaction)
+ FakeMailer. The HTTP layer is not involved. This level tests business logic and
domain exception boundaries in isolation from transport concerns.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models import Subscriber
from packages.newsletter.exceptions import (
    EmailAlreadySubscribed,
    SubscriptionCooldownError,
)
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.services.subscription import SubscriptionService
from tests.fakes.fake_mailer import FakeMailer


def make_service(
    db: AsyncSession, mailer: FakeMailer | None = None
) -> SubscriptionService:
    return SubscriptionService(
        subscriber_repository=SubscriberRepository(db),
        mailer=mailer or FakeMailer(),
    )


class TestRegister:
    async def test_creates_new_subscriber(
        self, db_session: AsyncSession, fake_mailer: FakeMailer
    ) -> None:
        service = make_service(db_session, fake_mailer)

        subscriber = await service.register("new@example.com")

        assert subscriber.email == "new@example.com"
        assert subscriber.subscribed is True

    async def test_sends_welcome_on_first_subscription(
        self, db_session: AsyncSession, fake_mailer: FakeMailer
    ) -> None:
        service = make_service(db_session, fake_mailer)

        await service.register("welcome@example.com")

        assert "welcome@example.com" in fake_mailer.sent_welcomes

    async def test_raises_if_already_subscribed(self, db_session: AsyncSession) -> None:
        service = make_service(db_session)
        await service.register("dup@example.com")

        with pytest.raises(EmailAlreadySubscribed):
            await service.register("dup@example.com")

    async def test_raises_cooldown_if_recently_unsubscribed(
        self, db_session: AsyncSession
    ) -> None:
        """Cooldown window is 30 days (see _is_within_cooldown).

        Note: the HTTP layer surfaces this as "You must wait 48 hours" —
        that message is stale and the cooldown logic should be aligned.
        """
        service = make_service(db_session)
        await service.register("cool@example.com")
        await service.unregister("cool@example.com")

        with pytest.raises(SubscriptionCooldownError):
            await service.register("cool@example.com")

    async def test_resubscribes_after_cooldown_expires(
        self, db_session: AsyncSession, fake_mailer: FakeMailer
    ) -> None:
        # Insert a subscriber whose cooldown has expired (31 days ago).
        # We bypass the service here because there's no public method to
        # create an unsubscribed subscriber with a custom timestamp.
        old_time = datetime.now(UTC) - timedelta(days=31)
        sub = Subscriber(
            email="resub@example.com",
            subscribed=False,
            unsubscribed_at=old_time,
        )
        db_session.add(sub)
        await (
            db_session.flush()
        )  # visible within this transaction; not committed to DB yet

        service = make_service(db_session, fake_mailer)
        result = await service.register("resub@example.com")

        assert result.subscribed is True
        # Welcome is NOT sent on re-subscription — only on brand-new subscribers.
        assert "resub@example.com" not in fake_mailer.sent_welcomes

    async def test_mailer_error_is_swallowed(self, db_session: AsyncSession) -> None:
        """A MailerError from send_welcome is logged and swallowed by the service.

        The subscriber is still created successfully. This is intentional — a
        transient email provider failure should not roll back the subscription.
        """
        failing_mailer = FakeMailer(fail_on_welcome=True)
        service = make_service(db_session, failing_mailer)

        subscriber = await service.register("swallow@example.com")

        assert subscriber.email == "swallow@example.com"
        assert subscriber.subscribed is True

    async def test_resubscribes_when_unsubscribed_at_is_null(
        self, db_session: AsyncSession, fake_mailer: FakeMailer
    ) -> None:
        """Re-subscribe proceeds when the inactive row has no unsubscribed_at.

        _is_within_cooldown returns False for a null unsubscribed_at, so the
        cooldown check does not block re-subscription (e.g. legacy/edge rows).
        """
        db_session.add(
            Subscriber(
                email="nullts@example.com",
                subscribed=False,
                unsubscribed_at=None,
            )
        )
        await db_session.flush()

        service = make_service(db_session, fake_mailer)
        result = await service.register("nullts@example.com")

        assert result.subscribed is True
        # Re-subscription never sends a welcome (only brand-new subscribers do).
        assert "nullts@example.com" not in fake_mailer.sent_welcomes


class TestUnregister:
    async def test_marks_subscriber_as_unsubscribed(
        self, db_session: AsyncSession
    ) -> None:
        service = make_service(db_session)
        await service.register("unsub@example.com")

        await service.unregister("unsub@example.com")

        repo = SubscriberRepository(db_session)
        sub = await repo.get_by_email("unsub@example.com")
        assert sub is not None
        assert sub.subscribed is False
        assert sub.unsubscribed_at is not None

    async def test_raises_if_subscriber_not_found(
        self, db_session: AsyncSession
    ) -> None:
        from packages.newsletter.exceptions import SubscriberNotFound

        service = make_service(db_session)

        with pytest.raises(SubscriberNotFound):
            await service.unregister("ghost@example.com")

    async def test_noop_when_already_unsubscribed_keeps_cooldown(
        self, db_session: AsyncSession
    ) -> None:
        """unregister is a no-op when the subscriber is already inactive.

        Re-running soft_delete would reset unsubscribed_at and restart the
        30-day cooldown; the guard returns early instead, leaving it untouched.
        """
        original = datetime(2026, 1, 1, tzinfo=UTC)
        db_session.add(
            Subscriber(
                email="alreadyoff@example.com",
                subscribed=False,
                unsubscribed_at=original,
            )
        )
        await db_session.flush()

        service = make_service(db_session)
        await service.unregister("alreadyoff@example.com")  # no exception raised

        repo = SubscriberRepository(db_session)
        sub = await repo.get_by_email("alreadyoff@example.com")
        assert sub is not None
        assert sub.unsubscribed_at == original  # cooldown clock not reset


class TestStats:
    async def test_counts_only_active_subscribers(
        self, db_session: AsyncSession
    ) -> None:
        now = datetime.now(UTC)
        db_session.add_all(
            [
                Subscriber(email="a1@example.com", subscribed=True, created_at=now),
                Subscriber(email="a2@example.com", subscribed=True, created_at=now),
                Subscriber(email="off@example.com", subscribed=False, created_at=now),
            ]
        )
        await db_session.flush()

        service = make_service(db_session)
        result = await service.stats()

        assert result.total_subscribers == 2

    async def test_joined_this_week_excludes_older_than_7_days(
        self, db_session: AsyncSession
    ) -> None:
        now = datetime.now(UTC)
        old = now - timedelta(days=10)
        db_session.add_all(
            [
                Subscriber(email="recent@example.com", subscribed=True, created_at=now),
                Subscriber(email="oldie@example.com", subscribed=True, created_at=old),
            ]
        )
        await db_session.flush()

        service = make_service(db_session)
        result = await service.stats()

        assert result.total_subscribers == 2
        assert result.joined_this_week == 1

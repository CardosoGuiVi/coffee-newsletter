import logging
from datetime import UTC, datetime, timedelta

from packages.database.models import Subscriber
from packages.mailer.base import Mailer
from packages.mailer.exceptions import MailerError
from packages.newsletter.exceptions import (
    EmailAlreadySubscribed,
    SubscriberNotFound,
    SubscriptionCooldownError,
)
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.schemas import StatsResult

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(
        self, subscriber_repository: SubscriberRepository, mailer: Mailer
    ) -> None:
        self.subscriber_repository = subscriber_repository
        self.mailer = mailer

    def _is_within_cooldown(self, unsubscribed_at: datetime | None) -> bool:
        if unsubscribed_at is None:
            return False
        return datetime.now(UTC) - unsubscribed_at < timedelta(days=30)

    async def _send_welcome(self, email: str) -> None:
        try:
            await self.mailer.send_welcome(email)
        except MailerError:
            logger.exception(f"Failed to send welcome email to {email}")

    async def register(self, email: str) -> Subscriber:
        existing = await self.subscriber_repository.get_by_email(email)

        if existing:
            if existing.subscribed:
                raise EmailAlreadySubscribed()
            if self._is_within_cooldown(existing.unsubscribed_at):
                raise SubscriptionCooldownError()
            return await self.subscriber_repository.update(existing)

        subscriber = await self.subscriber_repository.create(email)

        await self._send_welcome(email)
        return subscriber

    async def stats(self) -> StatsResult:
        since = datetime.now(UTC) - timedelta(days=7)
        total, joined = await self.subscriber_repository.get_stats(since)

        return StatsResult(total_subscribers=total, joined_this_week=joined)

    async def unregister(self, email: str) -> None:
        existing = await self.subscriber_repository.get_by_email(email)
        if not existing:
            raise SubscriberNotFound()

        # Idempotent no-op when already unsubscribed: re-running soft_delete
        # would reset unsubscribed_at and restart the 30-day re-subscribe
        # cooldown. Still returns None → the endpoint answers 200 either way.
        if not existing.subscribed:
            return

        await self.subscriber_repository.soft_delete(existing)

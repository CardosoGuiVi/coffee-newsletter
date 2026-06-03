from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.newsletter import Subscriber


class SubscriberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> Subscriber | None:
        result = await self.db.execute(
            select(Subscriber).where(
                Subscriber.email == email,
            )
        )

        return result.scalar_one_or_none()

    async def create(self, email: str) -> Subscriber:
        subscriber = Subscriber(email=email)
        self.db.add(subscriber)
        await self.db.commit()
        await self.db.refresh(subscriber)
        return subscriber

    async def update(self, subscriber: Subscriber) -> Subscriber:
        subscriber.subscribed = True
        subscriber.unsubscribed_at = None
        subscriber.created_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(subscriber)
        return subscriber

    async def soft_delete(self, subscriber: Subscriber) -> None:
        subscriber.subscribed = False
        subscriber.unsubscribed_at = datetime.now(UTC)
        subscriber.created_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(subscriber)

    async def list_active_subscribers(
        self,
    ) -> Sequence[Subscriber]:
        result = await self.db.execute(select(Subscriber).where(Subscriber.subscribed))

        return result.scalars().all()

    async def count_active(self) -> int:
        result = await self.db.execute(
            select(func.count()).where(Subscriber.subscribed)
        )
        return result.scalar_one()

    async def count_new_since(self, since: datetime) -> int:
        result = await self.db.execute(
            select(func.count()).where(
                Subscriber.subscribed, Subscriber.created_at >= since
            )
        )
        return result.scalar_one()

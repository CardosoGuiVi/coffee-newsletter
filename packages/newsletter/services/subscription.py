from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, UTC

from apps.api.schemas.newsletter import SubscribeRequest, StatsResponse, UnsubscribeRequest
from packages.database.models import Subscriber

from packages.newsletter.exceptions import (
    EmailAlreadySubscribed,
    SubscriptionCooldownError,
    SubscriberNotFound,
)


class SubscriptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db


    async def register(self, data: SubscribeRequest) -> Subscriber:
        subscriber = await self.db.scalar(
            select(Subscriber).where(Subscriber.email == data.email)
        )

        if subscriber:
            if subscriber.subscribed == 1:
                raise EmailAlreadySubscribed()
            
            cooldown = subscriber.unsubscribed_at + timedelta(hours=48)
            if datetime.now(UTC) < cooldown:
                raise SubscriptionCooldownError()
            
            subscriber.subscribed = 1
            subscriber.unsubscribed_at = None
            subscriber.created_at = datetime.now(UTC)

        else:
            subscriber = Subscriber(email = data.email)
            self.db.add(subscriber)
        
        await self.db.commit()
        await self.db.refresh(subscriber)
        return subscriber


    async def stats(self) -> StatsResponse:
        result_total = await self.db.execute(
            select(func.count()).select_from(Subscriber).where(Subscriber.subscribed == 1)
        )

        seven_days_ago = datetime.now(UTC) - timedelta(days=7)
        result_week = await self.db.execute(
            select(func.count())
            .select_from(Subscriber)
            .where(
                Subscriber.subscribed == 1,
                Subscriber.created_at >= seven_days_ago
            )
        )

        total:int = result_total.scalar()
        week:int = result_week.scalar()

        return StatsResponse(
            total_subscribers=total,
            joined_this_week=week
        )


    async def unregister(self, data: UnsubscribeRequest) -> bool:
        is_email_exists = await self.db.scalar(
            select(Subscriber).where(Subscriber.email == data.email)
        )

        if not is_email_exists:
            raise SubscriberNotFound()
        
        await self.db.execute(
            update(Subscriber)
            .where(Subscriber.email == data.email)
            .values(subscribed=0, unsubscribed_at=func.now())
        )
        await self.db.commit()

        return True
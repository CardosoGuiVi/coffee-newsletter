from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.newsletter import Subscriber


class SubscriberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_active_subscribers(
        self,
    ) -> Sequence[Subscriber]:
        result = await self.db.execute(
            select(Subscriber).where(
                Subscriber.subscribed == 1
            )
        )

        return result.scalars().all()

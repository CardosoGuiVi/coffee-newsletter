from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.session import get_session
from packages.newsletter.services.subscription import SubscriptionService


async def get_service(db: AsyncSession = Depends(get_session)) -> SubscriptionService:
    return SubscriptionService(db)

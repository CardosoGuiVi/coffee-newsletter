from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.session import get_session
from packages.mailer.providers.resend import ResendMailer
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.services.subscription import SubscriptionService


async def get_subscription_service(
    session: AsyncSession = Depends(get_session),
) -> SubscriptionService:
    return SubscriptionService(
        subscriber_repository=SubscriberRepository(session),
        mailer=ResendMailer(),
    )

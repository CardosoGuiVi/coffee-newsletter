import asyncio

from packages.database.session import AsyncSessionLocal
from packages.mailer.providers.resend import ResendMailer
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.services.campaign import CampaignService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        repository = SubscriberRepository(session)

        service = CampaignService(
            subscriber_repository=repository,
            mailer=ResendMailer(),
        )

        await service.send_newsletter()


if __name__ == "__main__":
    asyncio.run(main())

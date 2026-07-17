import asyncio
from typing import Any

from packages.database.session import AsyncSessionLocal, engine
from packages.mailer.providers.resend import ResendMailer
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.services.campaign import CampaignService


async def run(dry_run: bool = False, test_email: str | None = None) -> None:
    try:
        async with AsyncSessionLocal() as session:
            repository = SubscriberRepository(session)

            service = CampaignService(
                subscriber_repository=repository,
                mailer=ResendMailer(),
            )

            await service.send_newsletter(dry_run=dry_run, test_email=test_email)
    finally:
        # A fresh event loop is created per Lambda invocation (asyncio.run in
        # handler()); the pooled connections from a prior invocation's loop
        # would otherwise outlive it and break on the next warm invocation.
        await engine.dispose()


async def main() -> None:
    await run()


def handler(event: dict[str, Any] | None, context: Any) -> dict[str, str]:
    """AWS Lambda entrypoint, triggered weekly by EventBridge Scheduler.

    For manual verification via `aws lambda invoke --payload`:
      {"dry_run": true}                        — build the newsletter, send nothing
      {"test_email": "you@example.com"}         — send only to this address
    """
    event = event or {}
    dry_run = bool(event.get("dry_run", False))
    test_email = event.get("test_email")

    asyncio.run(run(dry_run=dry_run, test_email=test_email))

    return {"status": "ok"}


if __name__ == "__main__":
    asyncio.run(main())

import logging

from packages.core import settings
from packages.core.tokens import generate_unsubscribe_token
from packages.mailer.base import Mailer
from packages.newsletter.renderer import render_newsletter
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.summarizer import summarize_articles
from packages.scraper.rss import scrape_articles

logger = logging.getLogger(__name__)


DOMAIN: str = settings.API_URL


class CampaignService:
    def __init__(
        self,
        subscriber_repository: SubscriberRepository,
        mailer: Mailer,
    ) -> None:
        self.subscriber_repository = subscriber_repository
        self.mailer = mailer

    async def send_newsletter(self):
        articles = await scrape_articles()
        if not articles:
            logger.warning("No articles found. Aborting.")
            return

        newsletter = await summarize_articles(articles)

        html = render_newsletter(newsletter)

        subscribers = await self.subscriber_repository.list_active_subscribers()

        if not subscribers:
            logger.warning("No active subscribers found.")
            return

        for subscriber in subscribers:
            token = generate_unsubscribe_token(subscriber.email)
            unsubscribe_url = f"{DOMAIN}/v1/unsubscribe/one-click?email={subscriber.email}&token={token}"
            response = await self.mailer.send_email(
                subject=newsletter.subject,
                email=subscriber.email,
                html=html,
                unsubscribe_url=unsubscribe_url,
            )
            logger.info(response)

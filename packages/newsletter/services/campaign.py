import logging
from packages.mailer.base import Mailer
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.summarizer import summarize_articles
from packages.newsletter.renderer import render_newsletter
from packages.scraper.rss import scrape_articles


logger = logging.getLogger(__name__)


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
        
        subscribers = (
            await self.subscriber_repository
            .list_active_subscribers()
        )

        if not subscribers:
            logger.warning("No active subscribers found.")
            return
        
        for subscriber in subscribers:
            response = await self.mailer.send_email(
                newsletter.subject,
                subscriber.email,
                html
            )
            logger.info(response)

"""Unit tests for CampaignService.

CampaignService.send_newsletter() orchestrates four steps:
  1. scrape_articles()       — network I/O, patched here
  2. summarize_articles()    — Anthropic API, patched here
  3. render_newsletter()     — Jinja2, runs for real (fast, no I/O)
  4. mailer.send_email()     — FakeMailer

Why monkeypatch instead of injection?
scrape_articles and summarize_articles are imported as top-level names into
campaign.py, not passed as arguments. The service has no injection seam for
them. The correct patch target is the name *in the campaign module's namespace*:
  packages.newsletter.services.campaign.scrape_articles
  packages.newsletter.services.campaign.summarize_articles

FakeAIClient exists for tests that want to patch at a lower level
(inside summarize_articles itself). For this file we patch higher up.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models import Subscriber
from packages.newsletter.repository import SubscriberRepository
from packages.newsletter.schemas import Article, Newsletter, NewsletterItem
from packages.newsletter.services.campaign import CampaignService
from tests.fakes.fake_mailer import FakeMailer

FIXED_ARTICLES = [
    Article(
        title="Como preparar o espresso perfeito",
        url="https://perfectdailygrind.com/espresso",
        source="Perfect Daily Grind",
        summary="Um guia completo.",
    )
]

FIXED_NEWSLETTER = Newsletter(
    subject="☕ Seu café semanal chegou",
    intro="Essa semana trouxemos as melhores histórias.",
    week_label="Semana 25 · Junho 2026",
    items=[
        NewsletterItem(
            title="Como preparar o espresso perfeito",
            source="Perfect Daily Grind",
            url="https://perfectdailygrind.com/espresso",
            summary="Um guia completo.",
        )
    ],
    closing="Até semana que vem!",
)


@pytest.fixture
def patched_pipeline(monkeypatch):
    """Patches both network-bound functions in campaign.py's namespace."""

    async def fake_scrape():
        return FIXED_ARTICLES

    async def fake_summarize(_articles):
        return FIXED_NEWSLETTER

    monkeypatch.setattr(
        "packages.newsletter.services.campaign.scrape_articles", fake_scrape
    )
    monkeypatch.setattr(
        "packages.newsletter.services.campaign.summarize_articles", fake_summarize
    )


def make_campaign_service(db: AsyncSession, mailer: FakeMailer) -> CampaignService:
    return CampaignService(
        subscriber_repository=SubscriberRepository(db),
        mailer=mailer,
    )


class TestSendNewsletter:
    async def test_sends_to_all_active_subscribers(
        self,
        db_session: AsyncSession,
        fake_mailer: FakeMailer,
        patched_pipeline,
    ) -> None:
        db_session.add(Subscriber(email="sub1@example.com", subscribed=True))
        db_session.add(Subscriber(email="sub2@example.com", subscribed=True))
        db_session.add(Subscriber(email="inactive@example.com", subscribed=False))
        await db_session.flush()

        await make_campaign_service(db_session, fake_mailer).send_newsletter()

        assert len(fake_mailer.sent_emails) == 2
        sent_to = {e["email"] for e in fake_mailer.sent_emails}
        assert sent_to == {"sub1@example.com", "sub2@example.com"}

    async def test_email_contains_correct_subject(
        self,
        db_session: AsyncSession,
        fake_mailer: FakeMailer,
        patched_pipeline,
    ) -> None:
        db_session.add(Subscriber(email="reader@example.com", subscribed=True))
        await db_session.flush()

        await make_campaign_service(db_session, fake_mailer).send_newsletter()

        assert fake_mailer.sent_emails[0]["subject"] == FIXED_NEWSLETTER.subject

    async def test_unsubscribe_url_uses_one_click_endpoint(
        self,
        db_session: AsyncSession,
        fake_mailer: FakeMailer,
        patched_pipeline,
    ) -> None:
        """Each email must carry a signed one-click unsubscribe URL so email
        clients can surface the List-Unsubscribe header correctly."""
        db_session.add(Subscriber(email="reader@example.com", subscribed=True))
        await db_session.flush()

        await make_campaign_service(db_session, fake_mailer).send_newsletter()

        url = fake_mailer.sent_emails[0]["unsubscribe_url"]
        assert "/v1/unsubscribe/one-click" in url
        assert "token=" in url
        assert "email=reader@example.com" in url

    async def test_aborts_when_no_articles(
        self,
        db_session: AsyncSession,
        fake_mailer: FakeMailer,
        monkeypatch,
    ) -> None:
        """If scraping returns nothing, the pipeline stops before calling the AI
        or the mailer — no wasted API calls."""

        async def empty_scrape():
            return []

        monkeypatch.setattr(
            "packages.newsletter.services.campaign.scrape_articles", empty_scrape
        )

        db_session.add(Subscriber(email="sub@example.com", subscribed=True))
        await db_session.flush()

        await make_campaign_service(db_session, fake_mailer).send_newsletter()

        assert fake_mailer.sent_emails == []

    async def test_aborts_when_no_active_subscribers(
        self,
        db_session: AsyncSession,
        fake_mailer: FakeMailer,
        patched_pipeline,
    ) -> None:
        """No active subscribers → no emails sent, no error raised."""
        await make_campaign_service(db_session, fake_mailer).send_newsletter()

        assert fake_mailer.sent_emails == []

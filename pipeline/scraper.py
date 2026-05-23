import asyncio
import feedparser # type: ignore
from datetime import datetime, timedelta, UTC

from pipeline.schemas.scraper import Article
from app.core.config import settings
from app.core.consts import RSS_FEEDS



def is_recent(entry) -> bool:
    if not hasattr(entry, "published_parsed") or not entry.published_parsed:
        return True
    published = datetime(*entry.published_parsed[:6], tzinfo=UTC)
    return published >= datetime.now(UTC) - timedelta(days=settings.DAYS_BACK)


def parse_feed(source_name: str, feed_url: str) -> list[Article]:
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries:
            if not is_recent(entry):
                continue
            articles.append(Article(
                title=entry.get("title", "Sem título"),
                url=entry.get("link", ""),
                source=source_name,
                summary=entry.get("summary", "")[:500],
                published_at=entry.get("published", ""),
            ))
        return articles
    except Exception as e:
        print(f"⚠️  Erro ao buscar {source_name}: {e}")
        return []


async def fetch_all_feeds() -> list[Article]:
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, parse_feed, name, url)
        for name, url in RSS_FEEDS.items()
    ]
    results = await asyncio.gather(*tasks)
    all_articles = [a for feed in results for a in feed if a.url]
    print(f"Fontes consultadas: {len(RSS_FEEDS)}")
    return all_articles

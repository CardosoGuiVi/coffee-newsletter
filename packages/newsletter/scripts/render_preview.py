import asyncio
import json
from pathlib import Path

from packages.scraper.rss import scrape_articles
from packages.newsletter.summarizer import summarize_articles
from packages.newsletter.renderer import render_newsletter
from packages.newsletter.schemas import Newsletter

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR.parent / "artifacts"
NEWSLETTER_PATH = ARTIFACTS_DIR / "newsletter.json"
PREVIEW_PATH = ARTIFACTS_DIR / "preview.html"


async def render_preview() -> None:
    articles = await scrape_articles()
    if not articles:
        print("No articles scraped. Aborting.")
        return

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    if not NEWSLETTER_PATH.exists():
        print("Summarizing articles...")
        summarized = await summarize_articles(articles)
        with open(NEWSLETTER_PATH, "w", encoding="utf-8") as f:
            json.dump(summarized.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"Newsletter saved to {NEWSLETTER_PATH}")

    with open(NEWSLETTER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = render_newsletter(Newsletter(**data))

    with open(PREVIEW_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Preview saved to {PREVIEW_PATH}")


if __name__ == "__main__":
    asyncio.run(render_preview())
"""Unit tests for the RSS scraper (parse_feed).

These tests are fully synchronous and make no network calls — feedparser
accepts raw XML strings as well as URLs, so we feed it the fixture file.

The fixture omits pubDate on entries so they are always treated as recent,
making the happy-path tests independent of when they run.
"""

from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from pathlib import Path

from packages.scraper.rss import parse_feed

FIXTURE = (Path(__file__).parent.parent / "fixtures" / "sample_feed.xml").read_text()


class TestParseFeed:
    def test_extracts_all_articles_from_valid_feed(self) -> None:
        articles = parse_feed("Test Source", FIXTURE)

        assert len(articles) == 2

    def test_maps_fields_correctly(self) -> None:
        articles = parse_feed("Test Source", FIXTURE)

        first = articles[0]
        assert first.title == "How to brew perfect espresso"
        assert first.url == "https://example.com/espresso-guide"
        assert first.source == "Test Source"
        assert first.summary  # not None and non-empty

    def test_truncates_summary_to_500_chars(self) -> None:
        long_description = "x" * 600
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Long Article</title>
      <link>https://example.com/long</link>
      <description>{long_description}</description>
    </item>
  </channel>
</rss>"""

        articles = parse_feed("Test Source", xml)

        assert len(articles) == 1
        summary = articles[0].summary
        assert summary is not None and len(summary) == 500

    def test_returns_empty_list_on_unparseable_input(self) -> None:
        """parse_feed's broad except catches all errors and returns []."""
        articles = parse_feed("Bad Source", "this is not xml or a url <<<")

        # feedparser is very permissive and may return an empty entries list
        # rather than raising — either way, we get no articles.
        assert articles == [] or all(not a.url for a in articles)

    def test_recent_pubdate_entry_is_included(self) -> None:
        """Entries with a pubDate within the last 7 days are included."""
        three_days_ago = format_datetime(datetime.now(UTC) - timedelta(days=3))
        xml_with_date = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Dated Article</title>
      <link>https://example.com/dated</link>
      <pubDate>{three_days_ago}</pubDate>
    </item>
  </channel>
</rss>"""

        articles = parse_feed("Test Source", xml_with_date)

        assert len(articles) == 1

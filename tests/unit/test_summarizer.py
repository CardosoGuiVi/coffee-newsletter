"""Unit tests for enforce_source_diversity.

Guards against a single source dominating the final newsletter when the
model doesn't follow the "max 2 per source" prompt instruction — see
packages/newsletter/prompts.py.
"""

from packages.newsletter.schemas import NewsletterItem
from packages.newsletter.summarizer import enforce_source_diversity


def make_item(source: str, title: str = "Title") -> NewsletterItem:
    return NewsletterItem(
        title=title,
        source=source,
        url=f"https://example.com/{title}",
        summary="Resumo.",
    )


class TestEnforceSourceDiversity:
    def test_drops_items_beyond_max_per_source(self) -> None:
        items = [
            make_item("Source A", "1"),
            make_item("Source A", "2"),
            make_item("Source A", "3"),
            make_item("Source B", "4"),
        ]

        result = enforce_source_diversity(items)

        assert len(result) == 3
        assert [i.title for i in result] == ["1", "2", "4"]

    def test_keeps_all_items_when_within_limit(self) -> None:
        items = [
            make_item("Source A", "1"),
            make_item("Source B", "2"),
            make_item("Source C", "3"),
        ]

        result = enforce_source_diversity(items)

        assert result == items

    def test_preserves_original_order(self) -> None:
        items = [
            make_item("Source A", "1"),
            make_item("Source B", "2"),
            make_item("Source A", "3"),
            make_item("Source A", "4"),
        ]

        result = enforce_source_diversity(items)

        assert [i.title for i in result] == ["1", "2", "3"]

    def test_respects_custom_max_per_source(self) -> None:
        items = [
            make_item("Source A", "1"),
            make_item("Source A", "2"),
            make_item("Source A", "3"),
        ]

        result = enforce_source_diversity(items, max_per_source=1)

        assert len(result) == 1
        assert result[0].title == "1"

    def test_empty_list_returns_empty_list(self) -> None:
        assert enforce_source_diversity([]) == []

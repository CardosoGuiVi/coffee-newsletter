"""Unit tests for the summarizer module.

enforce_source_diversity guards against a single source dominating the
final newsletter when the model doesn't follow the "max 2 per source"
prompt instruction — see packages/newsletter/prompts.py.
"""

import json

import pytest

from packages.newsletter.schemas import Article, NewsletterItem
from packages.newsletter.summarizer import (
    build_prompt,
    clean_claude_response,
    enforce_source_diversity,
    format_articles,
    summarize_articles,
)
from tests.fakes.fake_ai import FakeAIClient


def make_item(source: str, title: str = "Title") -> NewsletterItem:
    return NewsletterItem(
        title=title,
        source=source,
        url=f"https://example.com/{title}",
        summary="Resumo.",
    )


def make_article(source: str, title: str = "Title") -> Article:
    return Article(
        title=title,
        url=f"https://example.com/{title}",
        source=source,
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


class TestFormatArticles:
    def test_numbers_articles_from_one(self) -> None:
        articles = [make_article("Source A", "1"), make_article("Source B", "2")]

        text = format_articles(articles)

        assert "[1] Fonte: Source A" in text
        assert "[2] Fonte: Source B" in text

    def test_includes_title_url_and_summary(self) -> None:
        article = make_article("Source A", "Hello")

        text = format_articles([article])

        assert "Título: Hello" in text
        assert f"URL: {article.url}" in text
        assert "Resumo: Resumo." in text

    def test_missing_summary_falls_back_to_na(self) -> None:
        article = Article(
            title="No summary",
            url="https://example.com/no-summary",
            source="Source A",
            summary=None,
        )

        text = format_articles([article])

        assert "Resumo: N/A" in text

    def test_empty_list_returns_empty_string(self) -> None:
        assert format_articles([]) == ""


class TestBuildPrompt:
    def test_embeds_articles_text_in_prompt(self) -> None:
        prompt = build_prompt("ARTIGOS_DE_TESTE")

        assert "ARTIGOS_DE_TESTE" in prompt
        assert "Coado" in prompt


class TestCleanClaudeResponse:
    def test_parses_plain_json(self) -> None:
        response = json.dumps({"key": "value"})

        assert clean_claude_response(response) == {"key": "value"}

    def test_strips_markdown_json_fence(self) -> None:
        response = f"```json\n{json.dumps({'key': 'value'})}\n```"

        assert clean_claude_response(response) == {"key": "value"}

    def test_strips_plain_markdown_fence(self) -> None:
        response = f"```\n{json.dumps({'key': 'value'})}\n```"

        assert clean_claude_response(response) == {"key": "value"}


class TestSummarizeArticles:
    async def test_returns_newsletter_built_from_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "packages.newsletter.summarizer.AnthropicClient",
            lambda: FakeAIClient(),
        )
        articles = [make_article("Perfect Daily Grind", "1")]

        newsletter = await summarize_articles(articles)

        assert newsletter.subject == "☕ Seu café semanal chegou"
        assert len(newsletter.items) == 1
        assert newsletter.items[0].source == "Perfect Daily Grind"

    async def test_applies_source_diversity_cap_to_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class OverConcentratedAIClient:
            async def generate(self, prompt: str) -> str:
                return json.dumps(
                    {
                        "subject": "Assunto",
                        "intro": "Intro",
                        "week_label": "Semana 1",
                        "items": [
                            {
                                "title": f"Item {i}",
                                "source": "Source A",
                                "url": f"https://example.com/{i}",
                                "summary": "Resumo.",
                            }
                            for i in range(4)
                        ],
                        "closing": "Até semana que vem!",
                    }
                )

        monkeypatch.setattr(
            "packages.newsletter.summarizer.AnthropicClient",
            lambda: OverConcentratedAIClient(),
        )
        articles = [make_article("Source A", str(i)) for i in range(4)]

        newsletter = await summarize_articles(articles)

        assert len(newsletter.items) == 2

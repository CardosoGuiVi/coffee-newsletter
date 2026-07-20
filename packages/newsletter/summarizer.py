import json
import random

from packages.ai.providers.anthropic import AnthropicClient
from packages.newsletter.prompts import PROMPT, PromptTemplate
from packages.newsletter.schemas import Article, Newsletter, NewsletterItem

# Mirrors the "no more than 2 per source" instruction in the prompt — the
# prompt asks the model to do this, this enforces it regardless of whether
# it complies.
MAX_ITEMS_PER_SOURCE: int = 2


def format_articles(articles: list[Article]) -> str:
    return "\n\n".join(
        [
            f"[{i + 1}] Fonte: {a.source}\n"
            f"Título: {a.title}\n"
            f"URL: {a.url}\n"
            f"Resumo: {a.summary or 'N/A'}"
            for i, a in enumerate(articles)
        ]
    )


def build_prompt(articles_text: str) -> str:
    return PROMPT.format_map(vars(PromptTemplate(articles_text=articles_text)))


def clean_claude_response(response: str):
    if response.startswith("```"):
        response = response.split("```")[1]

        if response.startswith("json"):
            response = response[4:]

    return json.loads(response)


def enforce_source_diversity(
    items: list[NewsletterItem], max_per_source: int = MAX_ITEMS_PER_SOURCE
) -> list[NewsletterItem]:
    counts: dict[str, int] = {}
    diverse_items = []
    for item in items:
        counts[item.source] = counts.get(item.source, 0) + 1
        if counts[item.source] <= max_per_source:
            diverse_items.append(item)
    return diverse_items


async def summarize_articles(
    articles: list[Article],
) -> Newsletter:
    shuffled_articles = random.sample(articles, len(articles))
    articles_text = format_articles(shuffled_articles)
    prompt = build_prompt(articles_text)
    response = await AnthropicClient().generate(prompt)
    data = clean_claude_response(response)

    newsletter = Newsletter(**data)
    newsletter.items = enforce_source_diversity(newsletter.items)
    return newsletter

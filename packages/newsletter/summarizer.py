import json

from packages.ai.claude import ClaudeClient
from packages.newsletter.prompts import PROMPT, PromptTemplate
from packages.newsletter.schemas import Article, Newsletter


def format_articles(articles: list[Article]) -> str:
    return "\n\n".join(
        [
            f"[{i + 1}] Fonte: {a.source}\n"
            f"Título: {a.title}\n"
            f"URL: {a.url}\n"
            f"Resumo: {a.summary or 'N/A'}"
            for i, a in enumerate(articles[:50])
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


async def summarize_articles(
    articles: list[Article],
) -> Newsletter:
    articles_text = format_articles(articles)
    prompt = build_prompt(articles_text)
    response = await ClaudeClient().generate(prompt)
    data = clean_claude_response(response)

    return Newsletter(**data)

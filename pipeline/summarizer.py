import json
import anthropic

from app.core.config import settings
from app.core.consts import PROMPT, PromptTemplate
from pipeline.scraper import Article
from pipeline.schemas.summarizer import Newsletter


async def generate_newsletter(articles: list[Article]) -> Newsletter:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    articles_text = "\n\n".join([
        f"[{i+1}] Fonte: {a.source}\nTítulo: {a.title}\nURL: {a.url}\nResumo: {a.summary or 'N/A'}"
        for i, a in enumerate(articles[:50])
    ])

    content = PROMPT.format_map(vars(PromptTemplate(articles_text=articles_text)))
    message = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CLAUDE_MAX_TOKENS,
        messages=[{
            "role": "user",
            "content": content
        }]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw)
    return Newsletter(**data)

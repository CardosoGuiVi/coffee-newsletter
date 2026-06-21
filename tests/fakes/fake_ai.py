import json

# A fixed newsletter payload that satisfies Newsletter(**data) in summarize_articles.
FIXED_NEWSLETTER_RESPONSE = json.dumps(
    {
        "subject": "☕ Seu café semanal chegou",
        "intro": "Essa semana trouxemos as melhores histórias do mundo do café.",
        "week_label": "Semana 25 · Junho 2026",
        "items": [
            {
                "title": "Como preparar o espresso perfeito",
                "source": "Perfect Daily Grind",
                "url": "https://perfectdailygrind.com/test",
                "summary": "Um guia completo para extrair o espresso ideal.",
            }
        ],
        "closing": "Até semana que vem!",
    }
)


class FakeAIClient:
    """Fake for AnthropicClient — same duck-type interface, no API calls.

    Note: AnthropicClient is a concrete class, not a Protocol. There is no
    injection seam in summarize_articles — it instantiates AnthropicClient()
    directly. To use this fake, patch at the import site:

        monkeypatch.setattr(
            "packages.newsletter.summarizer.AnthropicClient",
            lambda: FakeAIClient(),
        )

    For campaign-service-level tests it is cleaner to patch summarize_articles
    itself (see test_newsletter_service.py), which avoids going inside the
    summarizer module entirely.
    """

    async def generate(self, prompt: str) -> str:
        return FIXED_NEWSLETTER_RESPONSE

from anthropic import AsyncAnthropic

from packages.core import settings


class AnthropicClient:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.AI_PROVIDER.API_KEY)

    async def generate(self, prompt: str) -> str:
        response = await self.client.messages.create(
            model=settings.AI_PROVIDER.MODEL,
            max_tokens=settings.AI_PROVIDER.MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return response.content[0].text.strip()

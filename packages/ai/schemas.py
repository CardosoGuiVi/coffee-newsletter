from pydantic import BaseModel


class AnthropicSettings(BaseModel):
    MODEL: str = "claude-haiku-4-5-20251001"
    MAX_TOKENS: int = 2_000
    API_KEY: str

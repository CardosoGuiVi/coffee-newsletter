from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.database.schemas import DatabaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="COFFEE_",
        case_sensitive=True,
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Database
    DATABASE: DatabaseSettings

    # App
    APP_NAME: str = "Coado"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_URL: str

    # Pipeline
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"
    CLAUDE_MAX_TOKENS: int = 2000
    DAYS_BACK: int = 7
    ANTHROPIC_API_KEY: str
    RESEND_API_KEY: str
    FROM_EMAIL: str


settings = Settings()

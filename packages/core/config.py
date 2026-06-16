from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.ai.schemas import AnthropicSettings
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
    API_URL: str = Field(default="https://coffee.guicardoso.dev.br")

    # Providers
    AI_PROVIDER: AnthropicSettings
    RESEND_API_KEY: str
    FROM_EMAIL: str

    # Security
    ALLOWED_HOSTS: list[str] = Field(
        default=["coffee.guicardoso.dev.br", "localhost", "127.0.0.1"]
    )
    CORS_ORIGINS: list[str] = Field(default=["https://coffee.guicardoso.dev.br"])


settings = Settings()

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str
    DB: str
    PASSWORD: str

    @property
    def URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:"
            f"{self.PASSWORD}@{self.HOST}:"
            f"{self.PORT}/{self.DB}"
        )


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
    APP_NAME: str = "Coffee Newsletter"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_URL: str = "http://localhost:8000" if DEBUG else ""

    # Pipeline
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"
    CLAUDE_MAX_TOKENS: int = 2000
    DAYS_BACK: int = 7
    ANTHROPIC_API_KEY: str | None
    RESEND_API_KEY: str | None
    FROM_EMAIL: str | None


settings = Settings()

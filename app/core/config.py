from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

RSS_FEEDS = {
    "Revista Espresso": "https://revistaespresso.com.br/feed/",
    # "CaféPoint": "https://www.cafepoint.com.br/",# Criar um scraper para esse
    "CeCafé": "https://www.cecafe.com.br/feed/",
    "Revista Cafeicultura": "https://www.revistacafeicultura.com.br/feed/",
    "Blog do Café": "https://www.blogdocafe.com.br/feeds/posts/default?alt=rss",
    "Coffee & Joy Blog": "https://blog.coffeeandjoy.com.br/feed/",
    "Perfect Daily Grind": "https://perfectdailygrind.com/feed/",
    "Daily Coffee News": "https://dailycoffeenews.com/feed/",
    "Sprudge": "https://sprudge.com/feed/",
    "Fresh Cup": "https://freshcup.com/feed/",
    "SCA News": "https://sca.coffee/sca-news?format=rss",
    "Barista Magazine": "https://www.baristamagazine.com/feed/",
    "Coffee Chronicler": "https://coffeechronicler.com/feed/",
    "r/Coffee": "https://www.reddit.com/r/Coffee.rss",
    "r/CafeEspecialBR": "https://www.reddit.com/r/CafeEspecialBR.rss"
}

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

    # Pipeline
    RSS_FEEDS: dict[str, str] = RSS_FEEDS
    DAYS_BACK: int = 7


settings = Settings()

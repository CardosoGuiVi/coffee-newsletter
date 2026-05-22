from pydantic import BaseModel


class Article(BaseModel):
    title: str
    url: str
    source: str
    summary: str | None = None
    published_at: str | None = None

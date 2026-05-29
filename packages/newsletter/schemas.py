from pydantic import BaseModel


class Article(BaseModel):
    title: str
    url: str
    source: str
    summary: str | None = None
    published_at: str | None = None

class NewsletterItem(BaseModel):
    title: str
    source: str
    url: str
    summary: str


class Newsletter(BaseModel):
    subject: str
    intro: str
    items: list[NewsletterItem]
    closing: str
    week_label: str

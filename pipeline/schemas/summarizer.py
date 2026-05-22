from pydantic import BaseModel


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

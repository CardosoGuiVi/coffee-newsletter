from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from pipeline.schemas.summarizer import Newsletter


BASE_DIR = Path("templates")
TEMPLATES_DIR = BASE_DIR / "emails"

URL_SUBSCRIBER: str = settings.API_URL
URL_UNSUBSCRIBER: str = settings.API_URL + "/unsubscribe"


env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)

def render_html(newsletter: Newsletter) -> str:
    template = env.get_template("newsletter.html")
    return template.render(
        week_label=newsletter.week_label,
        intro=newsletter.intro,
        items=newsletter.items,
        closing=newsletter.closing,
        refer_url=URL_SUBSCRIBER,
        unsubscribe_url=URL_UNSUBSCRIBER,
    )

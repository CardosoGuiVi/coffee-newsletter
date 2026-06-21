from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from packages.core import settings
from packages.newsletter.schemas import Newsletter

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"


env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def render_newsletter(newsletter: Newsletter) -> str:
    template = env.get_template("newsletter.html")

    return template.render(
        url_api=settings.API_URL,
        week_label=newsletter.week_label,
        intro=newsletter.intro,
        items=newsletter.items,
        closing=newsletter.closing,
        refer_url=settings.API_URL,
        unsubscribe_url=f"{settings.API_URL}/unsubscribe",
    )


def render_welcome(name: str | None = None) -> str:
    template = env.get_template("welcome.html")

    return template.render(url_api=settings.API_URL, url_web=settings.BASE_URL)

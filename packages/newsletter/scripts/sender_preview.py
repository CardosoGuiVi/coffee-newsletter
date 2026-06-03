import asyncio
import json
from pathlib import Path

from packages.mailer.providers.resend import ResendMailer
from packages.newsletter.renderer import render_newsletter
from packages.newsletter.schemas import Newsletter

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR.parent / "artifacts"
NEWSLETTER_PATH = ARTIFACTS_DIR / "newsletter.json"


async def send_email_preview():
    if not NEWSLETTER_PATH.exists():
        return

    with open(NEWSLETTER_PATH, encoding="utf-8") as f:
        data = json.load(f)

    newsletter = Newsletter(**data)
    html = render_newsletter(newsletter)

    mailer = ResendMailer()
    await mailer.send_email(
        subject=newsletter.subject, email="cardoso.guivi@gmail.com", html=html
    )


if __name__ == "__main__":
    asyncio.run(send_email_preview())

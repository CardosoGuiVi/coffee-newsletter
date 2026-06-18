import argparse
import asyncio
import json
from pathlib import Path

from packages.core.tokens import generate_unsubscribe_token
from packages.mailer.providers.resend import ResendMailer
from packages.newsletter.renderer import render_newsletter
from packages.newsletter.schemas import Newsletter

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR.parent / "artifacts"
NEWSLETTER_PATH = ARTIFACTS_DIR / "newsletter.json"


DOMAIN: str = "https://coffee.guicardoso.dev.br"
TEST_EMAIL = "cardoso.guivi@gmail.com"


async def send_newsletter():
    if not NEWSLETTER_PATH.exists():
        print(f"Newsletter not found at {NEWSLETTER_PATH}")
        return

    with open(NEWSLETTER_PATH, encoding="utf-8") as f:
        data = json.load(f)

    newsletter = Newsletter(**data)
    html = render_newsletter(newsletter)
    mailer = ResendMailer()

    token = generate_unsubscribe_token(TEST_EMAIL)
    unsubscribe_url = (
        f"{DOMAIN}/v1/unsubscribe/one-click?email={TEST_EMAIL}&token={token}"
    )
    await mailer.send_email(
        subject=newsletter.subject,
        email=TEST_EMAIL,
        html=html,
        unsubscribe_url=unsubscribe_url,
    )


async def send_welcome() -> None:
    mailer = ResendMailer()

    await mailer.send_welcome(TEST_EMAIL)
    print(f"Welcome email sent to {TEST_EMAIL}")


async def main(command: str) -> None:
    match command:
        case "newsletter":
            await send_newsletter()
        case "welcome":
            await send_welcome()
        case _:
            print(f"Unknown command: {command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coado email preview sender")
    parser.add_argument(
        "command",
        choices=["newsletter", "welcome"],
        help="Which email to send: 'newsletter' or 'welcome'",
    )
    args = parser.parse_args()
    asyncio.run(main(args.command))

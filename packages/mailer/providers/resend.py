import resend

from packages.core import settings
from packages.mailer.exceptions import MailerError
from packages.newsletter.renderer import render_welcome


class ResendMailer:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    async def send_email(
        self,
        subject: str,
        email: str,
        html: str,
        unsubscribe_url: str,
    ) -> resend.Emails.SendResponse:
        params: resend.Emails.SendParams = {
            "from": settings.FROM_EMAIL_NEWSLETTER,
            "to": [email],
            "subject": subject,
            "html": html,
            "headers": {
                "List-Unsubscribe": f"<{unsubscribe_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        }

        try:
            return resend.Emails.send(params)
        except Exception as e:
            raise MailerError("Failed to send email") from e

    async def send_welcome(self, email: str) -> None:
        html = render_welcome()

        params: resend.Emails.SendParams = {
            "from": settings.FROM_EMAIL_WELCOME,
            "to": [email],
            "subject": "☕ Bem-vindo. Seu café está quase pronto.",
            "html": html,
        }

        try:
            resend.Emails.send(params)
        except Exception as e:
            raise MailerError("Failed to send email") from e

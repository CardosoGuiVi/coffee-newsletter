import resend

from packages.core.config import settings
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
    ) -> resend.Emails.SendResponse:
        params: resend.Emails.SendParams = {
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": subject,
            "html": html,
            "headers": {
                "List-Unsubscribe": f"<{settings.API_URL}/unsubscribe>",
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
            "from": settings.FROM_EMAIL,  # Change to welcome@coado.club
            "to": [email],
            "subject": "Apenas um teste",
            "html": html,
            "headers": {
                "List-Unsubscribe": f"<{settings.API_URL}/unsubscribe>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        }

        try:
            await resend.Emails.send(params)
        except Exception as e:
            raise MailerError("Failed to send email") from e

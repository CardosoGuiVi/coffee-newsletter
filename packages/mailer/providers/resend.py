import resend

from packages.core.config import settings


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
        }

        return resend.Emails.send(params)

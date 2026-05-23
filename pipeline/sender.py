import resend

from app.core.config import settings


def send_email(subject: str, email: str, html: str) -> resend.Emails.SendResponse:
    resend.api_key = settings.RESEND_API_KEY
    params: resend.Emails.SendParams = {
        "from": settings.FROM_EMAIL,
        "to": [email],
        "subject": subject,
        "html": html,
    }
    return resend.Emails.send(params)

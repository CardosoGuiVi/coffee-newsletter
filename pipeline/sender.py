import resend
from resend import Emails

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.subscriber import SubscriberService


def send_email(subject: str, email: str, html: str) -> resend.Emails.SendResponse:
    resend.api_key = settings.RESEND_API_KEY
    params: resend.Emails.SendParams = {
        "from": settings.FROM_EMAIL,
        "to": [email],
        "subject": subject,
        "html": html,
    }
    return resend.Emails.send(params)


async def send_emails_to_active_subscribers(subject: str, html: str) -> list[dict[str, Emails.SendResponse]]:
    async with AsyncSessionLocal() as session:
        service = SubscriberService(session)
        subscribers = await service.list_active_subscribers()
        emails = [s.email for s in subscribers]
        responses = []
        for email in emails:
            response = send_email(subject, email, html)
            responses.append({ email: response })
    return responses

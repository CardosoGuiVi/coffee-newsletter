from packages.mailer.exceptions import MailerError


class FakeMailer:
    """In-memory stand-in for the Mailer protocol.

    Records every call so tests can assert on what was "sent" without touching
    Resend. Set fail_on_welcome=True to simulate a transient provider failure.
    """

    def __init__(self, *, fail_on_welcome: bool = False) -> None:
        self.sent_welcomes: list[str] = []
        self.sent_emails: list[dict] = []
        self.fail_on_welcome = fail_on_welcome

    async def send_welcome(self, email: str) -> None:
        if self.fail_on_welcome:
            raise MailerError("simulated welcome failure")
        self.sent_welcomes.append(email)

    async def send_email(
        self,
        subject: str,
        email: str,
        html: str,
        unsubscribe_url: str,
    ) -> None:
        self.sent_emails.append(
            {
                "subject": subject,
                "email": email,
                "html": html,
                "unsubscribe_url": unsubscribe_url,
            }
        )

from typing import Protocol, Any


class Mailer(Protocol):
    async def send_email(
        self,
        subject: str,
        email: str,
        html: str,
    ) -> Any: ...

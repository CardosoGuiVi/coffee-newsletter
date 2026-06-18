from typing import Any, Protocol


class Mailer(Protocol):
    async def send_email(
        self,
        subject: str,
        email: str,
        html: str,
        unsubscribe_url: str,
    ) -> Any: ...

    async def send_welcome(self, email: str) -> None: ...

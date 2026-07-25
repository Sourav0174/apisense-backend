from abc import ABC, abstractmethod


class EmailDeliveryError(Exception):
    """Raised when an EmailService implementation fails to send an email."""


class EmailService(ABC):
    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: str | None = None,
    ) -> None: ...

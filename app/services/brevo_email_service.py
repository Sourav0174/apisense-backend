import httpx

from app.services.email_service import EmailDeliveryError, EmailService

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoEmailService(EmailService):
    def __init__(self, api_key: str, sender_email: str, sender_name: str) -> None:
        self._api_key = api_key
        self._sender_email = sender_email
        self._sender_name = sender_name

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: str | None = None,
    ) -> None:
        recipient: dict[str, str] = {"email": to_email}
        if to_name:
            recipient["name"] = to_name

        payload = {
            "sender": {"email": self._sender_email, "name": self._sender_name},
            "to": [recipient],
            "subject": subject,
            "htmlContent": html_content,
        }
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BREVO_API_URL, json=payload, headers=headers)
        except httpx.RequestError as exc:
            # Covers ConnectError, TimeoutException, TransportError, and any other
            # network-level failure — all must surface as EmailDeliveryError so callers
            # (e.g. registration) can degrade gracefully instead of raising an unhandled error.
            raise EmailDeliveryError(f"Failed to reach Brevo API: {exc}") from exc

        if response.status_code >= 400:
            raise EmailDeliveryError(f"Brevo API error {response.status_code}: {response.text}")

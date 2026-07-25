import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.auth import TokenPayload

settings = get_settings()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenError(Exception):
    """Raised when a JWT is missing, malformed, expired, or of the wrong type."""


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_token(raw_token: str) -> str:
    """Fast, deterministic hash for lookup tokens (verification/reset). Not for passwords."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _create_token(subject: uuid.UUID | str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: uuid.UUID | str) -> str:
    return _create_token(
        subject,
        timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
    )


def decode_token(token: str, expected_type: str) -> TokenPayload:
    try:
        claims = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    try:
        payload = TokenPayload(**claims)
    except ValidationError as exc:
        raise TokenError("Malformed token payload") from exc

    if payload.type != expected_type:
        raise TokenError(f"Expected a {expected_type} token, got {payload.type!r}")

    return payload

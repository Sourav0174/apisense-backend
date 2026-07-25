import asyncio
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, hash_token, verify_password
from app.db.models.email_verification_token import EmailVerificationToken
from app.db.models.password_reset_token import PasswordResetToken
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import AuthProvider, User
from app.db.repositories.email_verification_token_repository import EmailVerificationTokenRepository
from app.db.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import RegisterRequest, Token
from app.schemas.user import UserCreate
from app.services.email_service import EmailDeliveryError, EmailService
from app.services.email_templates import password_reset_email_html, verification_email_html
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

settings = get_settings()


class InvalidCredentialsError(Exception):
    """Raised when login credentials don't match an active local-auth user."""


class EmailNotVerifiedError(Exception):
    """Raised when login is attempted before the account's email has been verified."""


class InvalidVerificationTokenError(Exception):
    """Raised when a verification token is unknown, expired, or already used."""


class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is unknown, expired, or already revoked (incl. reuse after rotation)."""


class InvalidPasswordResetTokenError(Exception):
    """Raised when a password reset token is unknown, expired, or already used."""


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_service: UserService,
        email_verification_repository: EmailVerificationTokenRepository,
        email_service: EmailService,
        refresh_token_repository: RefreshTokenRepository,
        password_reset_token_repository: PasswordResetTokenRepository,
    ) -> None:
        self._session = session
        self._user_service = user_service
        self._email_verification_repository = email_verification_repository
        self._email_service = email_service
        self._refresh_token_repository = refresh_token_repository
        self._password_reset_token_repository = password_reset_token_repository

    async def register(self, data: RegisterRequest) -> User:
        password_hash = await asyncio.to_thread(hash_password, data.password)
        user_create = UserCreate(
            full_name=data.full_name,
            email=data.email,
            auth_provider=AuthProvider.LOCAL,
        )
        user = await self._user_service.create_user(user_create, password_hash=password_hash)

        try:
            await self.send_verification_email(user)
        except EmailDeliveryError:
            # Account is already created; don't fail registration over a delivery hiccup.
            # The user can request a fresh link via /auth/resend-verification.
            logger.warning("Failed to send verification email to %s", user.email, exc_info=True)

        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._user_service.get_user_by_email(email)
        if user is None or user.password_hash is None:
            raise InvalidCredentialsError("Incorrect email or password")
        if not await asyncio.to_thread(verify_password, password, user.password_hash):
            raise InvalidCredentialsError("Incorrect email or password")
        if not user.is_active:
            raise InvalidCredentialsError("User account is inactive")
        if not user.is_verified:
            raise EmailNotVerifiedError("Email address has not been verified")
        return await self._user_service.record_login(user.id)

    async def issue_tokens(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
        *,
        commit: bool = True,
    ) -> Token:
        raw_refresh_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.refresh_token_expire_minutes
        )
        await self._refresh_token_repository.create(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(raw_refresh_token),
                expires_at=expires_at,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        if commit:
            await self._session.commit()
        return Token(access_token=create_access_token(user.id), refresh_token=raw_refresh_token)

    async def refresh_tokens(
        self, raw_refresh_token: str, user_agent: str | None = None, ip_address: str | None = None
    ) -> Token:
        token = await self._refresh_token_repository.get_by_token_hash(hash_token(raw_refresh_token))
        if (
            token is None
            or token.revoked_at is not None
            or token.expires_at < datetime.now(timezone.utc)
        ):
            raise InvalidRefreshTokenError("Refresh token is invalid, expired, or revoked")

        await self._refresh_token_repository.record_usage(token)
        await self._refresh_token_repository.revoke(token)
        user = await self._user_service.get_user(token.user_id)

        # Revoking the old token and issuing the new one must land in one transaction —
        # a crash between them must never leave the user with zero valid refresh tokens.
        tokens = await self.issue_tokens(user, user_agent=user_agent, ip_address=ip_address, commit=False)
        await self._session.commit()
        return tokens

    async def revoke_refresh_token(self, raw_refresh_token: str) -> None:
        token = await self._refresh_token_repository.get_by_token_hash(hash_token(raw_refresh_token))
        if token is not None and token.revoked_at is None:
            await self._refresh_token_repository.revoke(token)
            await self._session.commit()

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        await self._refresh_token_repository.revoke_all_for_user(user_id)
        await self._session.commit()

    async def send_verification_email(self, user: User) -> None:
        await self._email_verification_repository.invalidate_active_for_user(user.id)

        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.email_verification_token_expire_hours
        )
        await self._email_verification_repository.create(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=expires_at,
            )
        )
        # Invalidating old tokens and issuing the new one must land in one transaction,
        # for the same reason as refresh-token rotation above.
        await self._session.commit()

        verification_link = f"{settings.app_base_url}/verify-email?token={raw_token}"
        html_content = verification_email_html(
            full_name=user.full_name,
            verification_link=verification_link,
            expire_hours=settings.email_verification_token_expire_hours,
        )
        await self._email_service.send_email(
            to_email=user.email,
            to_name=user.full_name,
            subject="Verify your APISense email address",
            html_content=html_content,
        )

    async def verify_email(self, raw_token: str) -> User:
        token = await self._email_verification_repository.get_by_token_hash(hash_token(raw_token))
        if (
            token is None
            or token.used_at is not None
            or token.expires_at < datetime.now(timezone.utc)
        ):
            raise InvalidVerificationTokenError("Verification token is invalid or expired")

        await self._email_verification_repository.mark_used(token)
        # Consuming the token and verifying the user must land in one transaction.
        user = await self._user_service.mark_email_verified(token.user_id, commit=False)
        await self._session.commit()
        return user

    async def resend_verification_email(self, email: str) -> None:
        user = await self._user_service.get_user_by_email(email)
        if user is None or user.is_verified:
            return
        await self.send_verification_email(user)

    async def forgot_password(self, email: str) -> None:
        # Deliberately silent on all "not eligible" cases (unknown email, unverified account)
        # so the router can return an identical response and avoid leaking account existence.
        user = await self._user_service.get_user_by_email(email)
        if user is None or not user.is_verified or not user.is_active:
            return

        await self._password_reset_token_repository.invalidate_active_for_user(user.id)

        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.password_reset_token_expire_minutes
        )
        await self._password_reset_token_repository.create(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=expires_at,
            )
        )
        # Invalidating old tokens and issuing the new one must land in one transaction,
        # for the same reason as email-verification and refresh-token rotation above.
        await self._session.commit()

        reset_link = f"{settings.app_base_url}/reset-password?token={raw_token}"
        html_content = password_reset_email_html(
            full_name=user.full_name,
            reset_link=reset_link,
            expire_minutes=settings.password_reset_token_expire_minutes,
        )
        try:
            await self._email_service.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="Reset your APISense password",
                html_content=html_content,
            )
        except EmailDeliveryError:
            # The reset token already exists; don't let a delivery hiccup change the
            # router's response. The user can request a fresh link if the email never arrives.
            logger.warning("Failed to send password reset email to %s", user.email, exc_info=True)

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        token = await self._password_reset_token_repository.get_by_token_hash(hash_token(raw_token))
        if (
            token is None
            or token.used_at is not None
            or token.expires_at < datetime.now(timezone.utc)
        ):
            raise InvalidPasswordResetTokenError("Password reset token is invalid or expired")

        password_hash = await asyncio.to_thread(hash_password, new_password)

        # Consuming the token, updating the password, and revoking every refresh token
        # must land in one transaction — a crash mid-way must never leave the account with
        # a changed password but still-valid old sessions, or a used token with no change applied.
        await self._password_reset_token_repository.mark_used(token)
        await self._user_service.update_password_hash(token.user_id, password_hash, commit=False)
        await self._refresh_token_repository.revoke_all_for_user(token.user_id)
        await self._session.commit()

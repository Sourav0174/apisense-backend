from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import TokenError, decode_token
from app.db.models.user import User
from app.db.repositories.email_verification_token_repository import EmailVerificationTokenRepository
from app.db.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.brevo_email_service import BrevoEmailService
from app.services.email_service import EmailService
from app.services.health_service import HealthService
from app.services.user_service import UserNotFoundError, UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    session: AsyncSession = Depends(get_db),
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository, session)


def get_email_verification_repository(
    session: AsyncSession = Depends(get_db),
) -> EmailVerificationTokenRepository:
    return EmailVerificationTokenRepository(session)


def get_refresh_token_repository(session: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_password_reset_token_repository(
    session: AsyncSession = Depends(get_db),
) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(session)


def get_email_service() -> EmailService:
    settings = get_settings()
    return BrevoEmailService(
        api_key=settings.brevo_api_key,
        sender_email=settings.email_from,
        sender_name=settings.email_from_name,
    )


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    email_verification_repository: EmailVerificationTokenRepository = Depends(
        get_email_verification_repository
    ),
    email_service: EmailService = Depends(get_email_service),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    password_reset_token_repository: PasswordResetTokenRepository = Depends(
        get_password_reset_token_repository
    ),
) -> AuthService:
    return AuthService(
        session,
        user_service,
        email_verification_repository,
        email_service,
        refresh_token_repository,
        password_reset_token_repository,
    )


def get_health_service(session: AsyncSession = Depends(get_db)) -> HealthService:
    return HealthService(session)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_payload = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise credentials_error from exc

    try:
        user = await user_service.get_user(token_payload.sub)
    except UserNotFoundError as exc:
        raise credentials_error from exc

    if not user.is_active:
        raise credentials_error

    return user

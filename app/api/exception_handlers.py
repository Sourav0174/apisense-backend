from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.auth_service import (
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidPasswordResetTokenError,
    InvalidRefreshTokenError,
    InvalidVerificationTokenError,
)
from app.services.health_service import DatabaseUnavailableError
from app.services.user_service import UserAlreadyExistsError


def _error(status_code: int, detail: str, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail}, headers=headers)


async def _handle_user_already_exists(request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return _error(status.HTTP_409_CONFLICT, "Email already registered")


async def _handle_invalid_credentials(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return _error(
        status.HTTP_401_UNAUTHORIZED,
        "Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _handle_email_not_verified(request: Request, exc: EmailNotVerifiedError) -> JSONResponse:
    return _error(status.HTTP_403_FORBIDDEN, "Email address has not been verified")


async def _handle_invalid_verification_token(
    request: Request, exc: InvalidVerificationTokenError
) -> JSONResponse:
    return _error(status.HTTP_400_BAD_REQUEST, "Verification token is invalid or expired")


async def _handle_invalid_refresh_token(request: Request, exc: InvalidRefreshTokenError) -> JSONResponse:
    return _error(status.HTTP_401_UNAUTHORIZED, "Invalid, expired, or revoked refresh token")


async def _handle_invalid_password_reset_token(
    request: Request, exc: InvalidPasswordResetTokenError
) -> JSONResponse:
    return _error(status.HTTP_400_BAD_REQUEST, "Password reset token is invalid or expired")


async def _handle_database_unavailable(request: Request, exc: DatabaseUnavailableError) -> JSONResponse:
    return _error(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unavailable")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserAlreadyExistsError, _handle_user_already_exists)
    app.add_exception_handler(InvalidCredentialsError, _handle_invalid_credentials)
    app.add_exception_handler(EmailNotVerifiedError, _handle_email_not_verified)
    app.add_exception_handler(InvalidVerificationTokenError, _handle_invalid_verification_token)
    app.add_exception_handler(InvalidRefreshTokenError, _handle_invalid_refresh_token)
    app.add_exception_handler(InvalidPasswordResetTokenError, _handle_invalid_password_reset_token)
    app.add_exception_handler(DatabaseUnavailableError, _handle_database_unavailable)

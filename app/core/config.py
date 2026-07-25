from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "APISense API"
    app_env: str = "development"

    database_url: str

    # SQLAlchemy connection pool tuning (defaults chosen for Neon's serverless Postgres).
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 300
    db_pool_pre_ping: bool = True
    db_echo: bool = False

    # JWT / auth settings.
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Brevo transactional email + verification link settings.
    brevo_api_key: str
    email_from: str
    email_from_name: str
    app_base_url: str
    email_verification_token_expire_hours: int = 24
    password_reset_token_expire_minutes: int = 30

    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize any postgres URL (plain, or an explicit driver like asyncpg) to psycopg,
        the async driver actually pinned in requirements.txt. psycopg wraps libpq, so Neon's
        sslmode / channel_binding query params work natively (asyncpg's connect() rejects them).
        """
        url = self.database_url
        for prefix in ("postgresql+asyncpg://", "postgresql+psycopg2://", "postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()

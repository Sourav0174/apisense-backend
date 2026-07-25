import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)


class DatabaseUnavailableError(Exception):
    """Raised when the health check's database query fails."""


class HealthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def check(self) -> HealthResponse:
        try:
            await self._session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            # Log the real cause internally; the client only ever sees a generic error.
            logger.exception("Database health check failed")
            raise DatabaseUnavailableError() from None
        return HealthResponse(status="ok", database="connected")

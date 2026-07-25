import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an email that's already registered."""


class UserNotFoundError(Exception):
    """Raised when a lookup or mutation targets a user id that doesn't exist."""


class UserService:
    def __init__(self, repository: UserRepository, session: AsyncSession) -> None:
        self._repository = repository
        self._session = session

    async def create_user(self, data: UserCreate, password_hash: str | None = None) -> User:
        if await self._repository.exists_by_email(data.email):
            raise UserAlreadyExistsError(data.email)
        user = User(
            full_name=data.full_name,
            email=data.email,
            avatar_url=data.avatar_url,
            auth_provider=data.auth_provider,
            password_hash=password_hash,
        )
        user = await self._repository.create(user)
        await self._session.commit()
        return user

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        return await self._repository.get_by_email(email)

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)
        updates = data.model_dump(exclude_unset=True)
        user = await self._repository.update(user, **updates)
        await self._session.commit()
        return user

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user(user_id)
        await self._repository.delete(user)
        await self._session.commit()

    async def record_login(self, user_id: uuid.UUID) -> User:
        user = await self.get_user(user_id)
        user = await self._repository.update(user, last_login=datetime.now(timezone.utc))
        await self._session.commit()
        return user

    async def mark_email_verified(self, user_id: uuid.UUID, *, commit: bool = True) -> User:
        user = await self.get_user(user_id)
        user = await self._repository.update(user, is_verified=True)
        if commit:
            await self._session.commit()
        return user

    async def update_password_hash(
        self, user_id: uuid.UUID, password_hash: str, *, commit: bool = True
    ) -> User:
        user = await self.get_user(user_id)
        user = await self._repository.update(user, password_hash=password_hash)
        if commit:
            await self._session.commit()
        return user

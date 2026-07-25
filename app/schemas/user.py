import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models.user import AuthProvider


class UserBase(BaseModel):
    full_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)
    avatar_url: str | None = Field(default=None, max_length=1024)


class UserCreate(UserBase):
    auth_provider: AuthProvider = AuthProvider.LOCAL


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=1024)
    is_active: bool | None = None
    is_verified: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    auth_provider: AuthProvider
    is_verified: bool
    is_active: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime

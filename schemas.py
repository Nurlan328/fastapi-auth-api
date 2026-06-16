"""Pydantic-схемы — описание данных, которые ВХОДЯТ в API и ВЫХОДЯТ из него.

Важно: схемы (что отдаём наружу) отделены от моделей БД.
Например, в UserOut НЕТ поля hashed_password — клиенту его знать незачем.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Что присылает клиент при регистрации."""
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Что мы отдаём клиенту (без пароля!)."""
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    # Позволяет создавать схему напрямую из ORM-объекта (user)
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Ответ при успешном логине."""
    access_token: str
    token_type: str = "bearer"

"""ORM-модели — описание таблиц в базе данных."""
from sqlalchemy import Column, DateTime, Integer, String, func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Внимание: храним ТОЛЬКО хеш пароля, никогда не сам пароль!
    hashed_password = Column(String, nullable=False)
    # Роль пользователя: "user" (обычный) или "admin".
    # По умолчанию все регистрируются как "user" — самому стать админом нельзя.
    role = Column(String, nullable=False, default="user", server_default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

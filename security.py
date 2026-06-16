"""Безопасность: хеширование паролей и работа с JWT-токенами."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import settings

# Настройки берём из единого config (а он — из .env / переменных окружения).
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# === ПАРОЛИ ===
def hash_password(password: str) -> str:
    """Превращает пароль в безопасный хеш (bcrypt сам добавляет случайную соль)."""
    pwd_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, что введённый пароль соответствует сохранённому хешу."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# === JWT-ТОКЕНЫ ===
def create_access_token(data: dict) -> str:
    """Создаёт подписанный JWT-токен с временем жизни."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

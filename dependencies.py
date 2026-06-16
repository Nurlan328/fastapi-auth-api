"""Зависимости (dependencies) для защиты эндпоинтов.

get_current_user — достаёт токен из заголовка Authorization, проверяет его
подпись и срок, находит пользователя ЧЕРЕЗ репозиторий (без прямого SQL).
Любой эндпоинт, который пропишет её через Depends, станет защищённым.
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import models
from repositories.user_repository import UserRepository, get_user_repository
from security import ALGORITHM, SECRET_KEY

# tokenUrl указывает, по какому адресу клиент получает токен (наш /auth/login).
# Именно это включает кнопку "Authorize" в Swagger (/docs).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        # Токен испорчен, с неверной подписью или просрочен
        raise credentials_exception

    user = users.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Пускает дальше ТОЛЬКО админа.

    Обрати внимание на разницу статусов:
      401 Unauthorized — «ты не залогинен / плохой токен» (это в get_current_user)
      403 Forbidden    — «ты залогинен, но прав не хватает» (вот это здесь)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user

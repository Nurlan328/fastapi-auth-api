"""Роуты пользователей — пример ЗАЩИЩЁННОГО эндпоинта."""
from fastapi import APIRouter, Depends

import models
import schemas
from dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    """Вернуть данные текущего пользователя.

    Сюда нельзя попасть без валидного токена — за это отвечает Depends(get_current_user).
    Если токена нет или он плохой — FastAPI сам вернёт 401.
    """
    return current_user

"""Роуты только для администраторов (контроллер). Пример ролевого доступа (RBAC).

Роутер тонкий — вся логика (включая кеширование статистики) в UserService.
"""
from fastapi import APIRouter, Depends

import schemas
from dependencies import get_current_admin
from services.user_service import UserService, get_user_service

# Зависимость get_current_admin висит на ВСЁМ роутере:
# любой эндпоинт здесь автоматически доступен только админу.
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(service: UserService = Depends(get_user_service)):
    """Список всех пользователей. Обычному юзеру вернёт 403."""
    return service.list_users()


@router.get("/stats")
async def stats(service: UserService = Depends(get_user_service)):
    """Статистика с кешированием. Поле "source" = cache | db."""
    return await service.get_stats()

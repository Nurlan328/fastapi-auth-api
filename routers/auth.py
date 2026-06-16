"""Роуты аутентификации — HTTP-эндпоинты входа и регистрации.

Роутер тонкий: принимает запрос, зовёт сервис, возвращает ответ.
Никакой бизнес-логики и SQL здесь нет — всё в service/repository.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

import schemas
from broker import get_email_publisher
from rate_limit import RateLimiter
from services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
    publish_email=Depends(get_email_publisher),
):
    """Регистрация: бизнес-логику делает сервис, контроллер лишь оркеструет."""
    new_user = service.register(user)

    # Планирование фоновой задачи — это HTTP-уровень (привязано к ответу),
    # поэтому остаётся в контроллере, а не в сервисе.
    background_tasks.add_task(
        publish_email, {"to": new_user.email, "username": new_user.username}
    )
    return new_user


@router.post(
    "/login",
    response_model=schemas.Token,
    # Rate limit как зависимость роута: 5 попыток за 60 секунд (защита от брутфорса).
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    """Логин: проверку пароля и выдачу токена делает сервис."""
    return service.login(form_data.username, form_data.password)

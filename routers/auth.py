"""Authentication routes — HTTP endpoints for login and registration.

The router is thin: it takes the request, calls the service, returns the response.
There is no business logic or SQL here — all of that lives in service/repository.
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
    """Registration: the service does the business logic, the route only orchestrates."""
    new_user = service.register(user)

    # Scheduling a background task is an HTTP-level concern (tied to the response),
    # so it stays in the route rather than the service.
    background_tasks.add_task(
        publish_email, {"to": new_user.email, "username": new_user.username}
    )
    return new_user


@router.post(
    "/login",
    response_model=schemas.Token,
    # Rate limit as a route dependency: 5 attempts per 60 seconds (brute-force protection).
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    """Login: the service checks the password and issues the token."""
    return service.login(form_data.username, form_data.password)

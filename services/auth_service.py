"""Authentication service — business logic for registration and login.

The service knows nothing about HTTP (Request/Response) and writes no SQL
directly. It orchestrates: asks the repository for data and applies the rules.
"""
from fastapi import Depends, HTTPException, status

import models
import schemas
from repositories.user_repository import UserRepository, get_user_repository
from security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, data: schemas.UserCreate) -> models.User:
        if self.users.get_by_username_or_email(data.username, data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username or email already exists",
            )
        return self.users.create(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )

    def login(self, username: str, password: str) -> schemas.Token:
        user = self.users.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.username})
        return schemas.Token(access_token=access_token)


def get_auth_service(users: UserRepository = Depends(get_user_repository)) -> AuthService:
    """FastAPI dependency — assembles the service with the needed repository."""
    return AuthService(users)

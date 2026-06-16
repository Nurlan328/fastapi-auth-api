"""User repository — the data-access layer.

Database queries (db.query...) live here and ONLY here. The rest of the app
works with users through this class's methods and doesn't know SQLAlchemy is
inside. Want to switch the DB? Only the repository changes.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

import models
from database import get_db


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> models.User | None:
        return (
            self.db.query(models.User)
            .filter(models.User.username == username)
            .first()
        )

    def get_by_username_or_email(self, username: str, email: str) -> models.User | None:
        return (
            self.db.query(models.User)
            .filter((models.User.username == username) | (models.User.email == email))
            .first()
        )

    def list_all(self) -> list[models.User]:
        return self.db.query(models.User).all()

    def count(self) -> int:
        return self.db.query(models.User).count()

    def create(self, *, username: str, email: str, hashed_password: str) -> models.User:
        user = models.User(username=username, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_role(self, user: models.User, role: str) -> models.User:
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """FastAPI dependency — returns a repository bound to the request's session."""
    return UserRepository(db)

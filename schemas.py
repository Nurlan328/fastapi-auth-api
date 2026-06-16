"""Pydantic schemas — the data that COMES IN to the API and GOES OUT of it.

Important: schemas (what we expose) are separate from the DB models.
For example, UserOut has no hashed_password field — the client doesn't need it.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """What the client sends on registration."""
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """What we return to the client (no password!)."""
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    # Allows building the schema directly from an ORM object (user)
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Response on a successful login."""
    access_token: str
    token_type: str = "bearer"

"""ORM models — description of the database tables."""
from sqlalchemy import Column, DateTime, Integer, String, func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Note: we store ONLY the password hash, never the password itself!
    hashed_password = Column(String, nullable=False)
    # User role: "user" (regular) or "admin".
    # Everyone registers as "user" by default — you can't make yourself an admin.
    role = Column(String, nullable=False, default="user", server_default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

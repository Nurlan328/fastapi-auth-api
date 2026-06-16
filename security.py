"""Security: password hashing and JWT tokens."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import settings

# Settings come from the single config (which reads .env / environment variables).
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# === PASSWORDS ===
def hash_password(password: str) -> str:
    """Turn a password into a safe hash (bcrypt adds a random salt itself)."""
    pwd_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check that the given password matches the stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# === JWT TOKENS ===
def create_access_token(data: dict) -> str:
    """Create a signed JWT token with an expiry."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

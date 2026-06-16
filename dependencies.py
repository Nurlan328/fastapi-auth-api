"""Dependencies for protecting endpoints.

get_current_user — pulls the token from the Authorization header, validates its
signature and expiry, and finds the user THROUGH the repository (no raw SQL).
Any endpoint that wires it via Depends becomes protected.
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import models
from repositories.user_repository import UserRepository, get_user_repository
from security import ALGORITHM, SECRET_KEY

# tokenUrl points to where the client obtains the token (our /auth/login).
# This is what enables the "Authorize" button in Swagger (/docs).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        # Token is malformed, has a bad signature, or is expired
        raise credentials_exception

    user = users.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Lets ONLY an admin through.

    Note the difference between statuses:
      401 Unauthorized — "you are not logged in / bad token" (in get_current_user)
      403 Forbidden    — "you are logged in but lack permissions" (here)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required",
        )
    return current_user

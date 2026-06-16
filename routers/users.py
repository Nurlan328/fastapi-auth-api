"""User routes — an example of a PROTECTED endpoint."""
from fastapi import APIRouter, Depends

import models
import schemas
from dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    """Return the current user's data.

    You can't get here without a valid token — that's what Depends(get_current_user)
    enforces. With no token or a bad one, FastAPI returns 401 on its own.
    """
    return current_user

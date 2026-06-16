"""Admin-only routes. An example of role-based access control (RBAC).

The router is thin — all logic (including stats caching) lives in UserService.
"""
from fastapi import APIRouter, Depends

import schemas
from dependencies import get_current_admin
from services.user_service import UserService, get_user_service

# get_current_admin sits on the WHOLE router:
# every endpoint here is automatically admin-only.
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(service: UserService = Depends(get_user_service)):
    """List all users. Returns 403 for a regular user."""
    return service.list_users()


@router.get("/stats")
async def stats(service: UserService = Depends(get_user_service)):
    """Stats with caching. The "source" field = cache | db."""
    return await service.get_stats()

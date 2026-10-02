from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.auth import AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
async def get_authenticated_user(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> AuthenticatedUser:
    return current_user

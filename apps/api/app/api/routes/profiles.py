from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProfileAlreadyExistsError, ProfileNotFoundError
from app.core.security import get_current_user
from app.db.session import get_session
from app.repositories.profiles import ProfileRepository
from app.schemas.auth import AuthenticatedUser
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.services.profiles import ProfileService

router = APIRouter(prefix="/profiles", tags=["Profiles"])


def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileService:
    profile_repository = ProfileRepository(session)
    return ProfileService(profile_repository)


@router.post(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_profile(
    data: ProfileCreate,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileResponse:
    try:
        profile = await service.create_profile(current_user.user_id, data)
        return profile
    except ProfileAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        ) from None


@router.get(
    "/me",
    response_model=ProfileResponse,
)
async def get_my_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileResponse:
    try:
        profile = await service.get_profile(current_user.user_id)
        return profile
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None

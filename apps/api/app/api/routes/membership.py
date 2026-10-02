from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidMembershipTransitionError,
    MembershipAlreadyExistsError,
    MembershipNotFoundError,
    OfferingNotFoundError,
    ProfileNotFoundError,
)
from app.core.security import get_current_user
from app.db.session import get_session
from app.repositories.membership import MembershipRepository
from app.repositories.offerings import OfferingRepository
from app.repositories.profiles import ProfileRepository
from app.schemas.auth import AuthenticatedUser
from app.schemas.membership import (
    MembershipResponse,
    MembershipUpdate,
)
from app.services.membership import MembershipService

router = APIRouter(tags=["Membership"])


def get_membership_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MembershipService:
    offering_repository = OfferingRepository(session)
    profile_repository = ProfileRepository(session)
    membership_repository = MembershipRepository(session)
    return MembershipService(
        profile_repository, offering_repository, membership_repository
    )


@router.post(
    "/offerings/{offering_id}/memberships/me",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_membership(
    offering_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MembershipService, Depends(get_membership_service)],
) -> MembershipResponse:
    try:
        membership = await service.create_membership(
            user_id=current_user.user_id, offering_id=offering_id
        )
        return membership
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None
    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offering not found",
        ) from None
    except MembershipAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Membership already exists"
        ) from None


@router.get(
    "/offerings/{offering_id}/memberships", response_model=list[MembershipResponse]
)
async def list_offering_memberships(
    offering_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MembershipService, Depends(get_membership_service)],
) -> list[MembershipResponse]:
    try:
        memberships = await service.list_offering_memberships(offering_id)
        return memberships
    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offering not found",
        ) from None


@router.get("/users/me/memberships", response_model=list[MembershipResponse])
async def list_user_memberships(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MembershipService, Depends(get_membership_service)],
) -> list[MembershipResponse]:
    try:
        memberships = await service.list_user_memberships(user_id=current_user.user_id)
        return memberships
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None


@router.get(
    "/offerings/{offering_id}/memberships/me", response_model=MembershipResponse
)
async def get_membership(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    offering_id: UUID,
    service: Annotated[MembershipService, Depends(get_membership_service)],
) -> MembershipResponse:
    try:
        membership = await service.get_membership(
            offering_id, user_id=current_user.user_id
        )
        return membership
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None
    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offering not found",
        ) from None
    except MembershipNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found",
        ) from None


@router.patch(
    "/offerings/{offering_id}/memberships/me",
    response_model=MembershipResponse,
)
async def update_membership(
    offering_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    data: MembershipUpdate,
    service: Annotated[MembershipService, Depends(get_membership_service)],
) -> MembershipResponse:
    try:
        return await service.update_membership_status(
            offering_id=offering_id,
            user_id=current_user.user_id,
            new_status=data.status,
        )
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None
    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offering not found",
        ) from None
    except MembershipNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found",
        ) from None
    except InvalidMembershipTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid membership status transition",
        ) from None

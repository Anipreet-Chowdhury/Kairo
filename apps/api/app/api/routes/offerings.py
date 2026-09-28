from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CourseNotFoundError,
    OfferingAlreadyExistsError,
    OfferingNotFoundError,
)
from app.db.models.course_offering import CourseOffering
from app.db.session import get_session
from app.repositories.course import CourseRepository
from app.repositories.offerings import OfferingRepository
from app.schemas.offerings import OfferingCreate, OfferingResponse
from app.services.offerings import OfferingService

router = APIRouter(tags=["Offerings"])


def get_offering_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OfferingService:
    offering_repository = OfferingRepository(session)
    course_repository = CourseRepository(session)
    return OfferingService(course_repository, offering_repository)


@router.post(
    "/courses/{course_id}/offerings",
    response_model=OfferingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_offering(
    course_id: UUID,
    data: OfferingCreate,
    service: Annotated[OfferingService, Depends(get_offering_service)],
) -> CourseOffering:
    try:
        offering = await service.create_offering(course_id, data)
        return offering
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        ) from None
    except OfferingAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Offering already exists",
        ) from None


@router.get("/courses/{course_id}/offerings", response_model=list[OfferingResponse])
async def list_course_offerings(
    course_id: UUID,
    service: Annotated[OfferingService, Depends(get_offering_service)],
) -> list[CourseOffering]:
    try:
        result = await service.list_course_offerings(course_id)
        return result
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        ) from None


@router.get(
    "/offerings/{offering_id}",
    response_model=OfferingResponse,
)
async def get_offering(
    offering_id: UUID,
    service: Annotated[OfferingService, Depends(get_offering_service)],
) -> CourseOffering:
    try:
        offering = await service.get_offering(offering_id)
        return offering
    except OfferingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offering not found",
        ) from None

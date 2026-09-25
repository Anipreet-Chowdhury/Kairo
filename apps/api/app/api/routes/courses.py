from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.courses import Course
from app.db.session import get_session
from app.repositories.course import CourseRepository
from app.schemas.course import CourseCreate, CourseResponse
from app.services.course import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


def get_course_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CourseService:
    repository = CourseRepository(session)
    return CourseService(repository)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> Course:
    course = await service.create_course(data)
    return course


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    service: Annotated[CourseService, Depends(get_course_service)],
) -> list[Course]:
    result = await service.list_courses()
    return result


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
)
async def get_course(
    course_id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> Course:
    try:
        course = await service.get_course(course_id)
        return course
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        ) from None

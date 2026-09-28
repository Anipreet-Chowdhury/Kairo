from uuid import UUID

from app.core.exceptions import (
    CourseNotFoundError,
    OfferingAlreadyExistsError,
    OfferingNotFoundError,
)
from app.db.models.course_offering import CourseOffering
from app.repositories.course import CourseRepository
from app.repositories.offerings import OfferingRepository
from app.schemas.offerings import OfferingCreate


class OfferingService:
    def __init__(
        self,
        course_repository: CourseRepository,
        offering_repository: OfferingRepository,
    ):
        self.course_repository = course_repository
        self.offering_repository = offering_repository

    async def create_offering(
        self, course_id: UUID, data: OfferingCreate
    ) -> CourseOffering:
        course = await self.course_repository.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError
        offering_exists = await self.offering_repository.already_exists(
            course_id, data.term, data.year
        )
        if offering_exists:
            raise OfferingAlreadyExistsError
        new_offering = await self.offering_repository.create(course_id, data)
        return new_offering

    async def list_course_offerings(self, course_id: UUID) -> list[CourseOffering]:
        course = await self.course_repository.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError
        course_list = await self.offering_repository.list_by_course(course_id)
        return course_list

    async def get_offering(self, offering_id: UUID) -> CourseOffering:
        offering = await self.offering_repository.get_by_id(offering_id)
        if offering is None:
            raise OfferingNotFoundError
        return offering

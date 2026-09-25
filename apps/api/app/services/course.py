from uuid import UUID

from app.db.models.courses import Course
from app.repositories.course import CourseRepository
from app.schemas.course import CourseCreate


class CourseService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository

    async def create_course(self, data: CourseCreate) -> Course:
        new_course = await self.repository.create(data)
        return new_course

    async def list_courses(self) -> list[Course]:
        course_list = await self.repository.list_all()
        return course_list

    async def get_course(self, course_id: UUID) -> Course:
        course = await self.repository.get_by_id(course_id)
        if course is None:
            raise ValueError("Course not found")
        return course

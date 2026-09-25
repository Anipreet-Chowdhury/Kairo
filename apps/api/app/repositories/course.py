from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.courses import Course
from app.schemas.course import CourseCreate


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: CourseCreate) -> Course:
        new_course = Course(**data.model_dump())

        self.session.add(new_course)
        await self.session.commit()
        await self.session.refresh(new_course)

        return new_course

    async def get_by_id(self, course_id: UUID) -> Course | None:
        statement = select(Course).where(Course.course_id == course_id)
        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_all(self) -> list[Course]:
        statement = select(Course)
        result = await self.session.execute(statement)

        return list(result.scalars())

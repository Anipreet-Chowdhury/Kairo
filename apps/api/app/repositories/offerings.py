from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_offering import CourseOffering
from app.db.models.enums import TermType
from app.schemas.offerings import OfferingCreate


class OfferingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, course_id: UUID, data: OfferingCreate) -> CourseOffering:
        new_offering = CourseOffering(course_id=course_id, **data.model_dump())

        self.session.add(new_offering)
        await self.session.commit()
        await self.session.refresh(new_offering)

        return new_offering

    async def get_by_id(self, offering_id: UUID) -> CourseOffering | None:
        statement = select(CourseOffering).where(
            CourseOffering.offering_id == offering_id
        )
        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_course(self, course_id: UUID) -> list[CourseOffering]:
        statement = select(CourseOffering).where(CourseOffering.course_id == course_id)
        result = await self.session.execute(statement)

        return list(result.scalars())

    async def already_exists(
        self,
        course_id: UUID,
        term: TermType,
        year: int,
    ) -> bool:
        statement = select(
            exists().where(
                CourseOffering.course_id == course_id,
                CourseOffering.year == year,
                CourseOffering.term == term,
            )
        )

        result = await self.session.execute(statement)
        return result.scalar_one()

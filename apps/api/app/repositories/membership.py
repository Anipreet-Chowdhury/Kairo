from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.course_membership import CourseMembership
from app.db.models.enums import MembershipStatus


class MembershipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, offering_id: UUID) -> CourseMembership:
        new_membership = CourseMembership(offering_id=offering_id, user_id=user_id)

        self.session.add(new_membership)
        await self.session.flush()
        await self.session.refresh(new_membership)

        return new_membership

    async def get_membership(
        self, user_id: UUID, offering_id: UUID
    ) -> CourseMembership | None:
        statement = select(CourseMembership).where(
            CourseMembership.offering_id == offering_id,
            CourseMembership.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_offering(self, offering_id: UUID) -> list[CourseMembership]:
        statement = select(CourseMembership).where(
            CourseMembership.offering_id == offering_id
        )
        result = await self.session.execute(statement)

        return list(result.scalars())

    async def list_by_user(self, user_id: UUID) -> list[CourseMembership]:
        statement = select(CourseMembership).where(CourseMembership.user_id == user_id)
        result = await self.session.execute(statement)

        return list(result.scalars())

    async def update_status(
        self, membership: CourseMembership, status: MembershipStatus, ended_at: datetime
    ) -> CourseMembership | None:
        statement = (
            update(CourseMembership)
            .where(
                CourseMembership.user_id == membership.user_id,
                CourseMembership.offering_id == membership.offering_id,
                CourseMembership.status == MembershipStatus.ACTIVE,
            )
            .values(
                status=status,
                ended_at=ended_at,
            )
            .returning(CourseMembership)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

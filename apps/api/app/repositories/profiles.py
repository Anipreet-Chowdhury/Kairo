from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.profile import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> Profile | None:
        statement = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

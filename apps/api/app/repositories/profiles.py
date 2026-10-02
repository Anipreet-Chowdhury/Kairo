from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.profile import Profile
from app.schemas.profile import ProfileCreate


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

    async def create(self, user_id: UUID, data: ProfileCreate) -> Profile:
        profile = Profile(user_id=user_id, **data.model_dump())

        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)

        return profile

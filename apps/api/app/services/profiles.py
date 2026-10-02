from uuid import UUID

from app.core.exceptions import ProfileAlreadyExistsError, ProfileNotFoundError
from app.db.models.profile import Profile
from app.repositories.profiles import ProfileRepository
from app.schemas.profile import ProfileCreate


class ProfileService:
    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    async def get_profile(self, user_id: UUID) -> Profile:
        profile = await self.profile_repository.get_by_id(user_id)
        if profile is None:
            raise ProfileNotFoundError
        return profile

    async def create_profile(self, user_id: UUID, data: ProfileCreate) -> Profile:
        existing_profile = await self.profile_repository.get_by_id(user_id)
        if existing_profile is not None:
            raise ProfileAlreadyExistsError
        new_profile = await self.profile_repository.create(user_id, data)
        return new_profile

from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import (
    InvalidMembershipTransitionError,
    MembershipAlreadyExistsError,
    MembershipNotFoundError,
    OfferingNotFoundError,
    ProfileNotFoundError,
)
from app.db.models.course_membership import CourseMembership
from app.db.models.enums import MembershipStatus
from app.repositories.membership import MembershipRepository
from app.repositories.offerings import OfferingRepository
from app.repositories.profiles import ProfileRepository


class MembershipService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        offering_repository: OfferingRepository,
        membership_repository: MembershipRepository,
    ):
        self.profile_repository = profile_repository
        self.offering_repository = offering_repository
        self.membership_repository = membership_repository

    async def create_membership(
        self, user_id: UUID, offering_id: UUID
    ) -> CourseMembership:
        profile = await self.profile_repository.get_by_id(user_id)
        if profile is None:
            raise ProfileNotFoundError
        offering = await self.offering_repository.get_by_id(offering_id)
        if offering is None:
            raise OfferingNotFoundError
        membership_exists = await self.membership_repository.get_membership(
            user_id, offering_id
        )
        if membership_exists:
            raise MembershipAlreadyExistsError
        new_membership = await self.membership_repository.create(user_id, offering_id)
        return new_membership

    async def list_offering_memberships(
        self, offering_id: UUID
    ) -> list[CourseMembership]:
        offering = await self.offering_repository.get_by_id(offering_id)
        if offering is None:
            raise OfferingNotFoundError
        membership_list = await self.membership_repository.list_by_offering(offering_id)
        return membership_list

    async def list_user_memberships(self, user_id: UUID) -> list[CourseMembership]:
        profile = await self.profile_repository.get_by_id(user_id)
        if profile is None:
            raise ProfileNotFoundError
        membership_list = await self.membership_repository.list_by_user(user_id)
        return membership_list

    async def get_membership(
        self, offering_id: UUID, user_id: UUID
    ) -> CourseMembership:
        profile = await self.profile_repository.get_by_id(user_id)
        if profile is None:
            raise ProfileNotFoundError
        offering = await self.offering_repository.get_by_id(offering_id)
        if offering is None:
            raise OfferingNotFoundError
        membership = await self.membership_repository.get_membership(
            user_id, offering_id
        )
        if membership is None:
            raise MembershipNotFoundError
        return membership

    async def update_membership_status(
        self,
        offering_id: UUID,
        user_id: UUID,
        new_status: MembershipStatus,
    ) -> CourseMembership:
        allowed_terminal_statuses = {
            MembershipStatus.COMPLETED,
            MembershipStatus.WITHDRAWN,
            MembershipStatus.REMOVED,
        }
        membership = await self.get_membership(offering_id, user_id)
        if (
            membership.status != MembershipStatus.ACTIVE
            or new_status not in allowed_terminal_statuses
        ):
            raise InvalidMembershipTransitionError
        updated_membership = await self.membership_repository.update_status(
            membership, new_status, datetime.now(UTC)
        )
        return updated_membership

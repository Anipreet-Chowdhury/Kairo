from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from app.api.routes.membership import get_membership_service, router
from app.core.exceptions import (
    InvalidMembershipTransitionError,
    MembershipAlreadyExistsError,
    MembershipNotFoundError,
    OfferingNotFoundError,
    ProfileNotFoundError,
)
from app.core.security import get_current_user
from app.db.models.course_membership import CourseMembership
from app.db.models.enums import MembershipStatus
from app.schemas.auth import AuthenticatedUser
from fastapi import FastAPI
from fastapi.testclient import TestClient

TEST_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
MISSING_USER_ID = UUID("22222222-2222-2222-2222-222222222222")


class FakeMembershipService:
    def __init__(self):
        self.memberships: dict[tuple[UUID, UUID], CourseMembership] = {}
        self.existing_profile_ids: set[UUID] = set()
        self.existing_offering_ids: set[UUID] = set()

    async def create_membership(
        self,
        user_id: UUID,
        offering_id: UUID,
    ) -> CourseMembership:
        if user_id not in self.existing_profile_ids:
            raise ProfileNotFoundError

        if offering_id not in self.existing_offering_ids:
            raise OfferingNotFoundError

        key = (user_id, offering_id)

        if key in self.memberships:
            raise MembershipAlreadyExistsError

        membership = CourseMembership(
            user_id=user_id,
            offering_id=offering_id,
            status=MembershipStatus.ACTIVE,
            joined_at=datetime.now(UTC),
            ended_at=None,
        )

        self.memberships[key] = membership
        return membership

    async def list_offering_memberships(
        self,
        offering_id: UUID,
    ) -> list[CourseMembership]:
        if offering_id not in self.existing_offering_ids:
            raise OfferingNotFoundError

        return [
            membership
            for membership in self.memberships.values()
            if membership.offering_id == offering_id
        ]

    async def list_user_memberships(
        self,
        user_id: UUID,
    ) -> list[CourseMembership]:
        if user_id not in self.existing_profile_ids:
            raise ProfileNotFoundError

        return [
            membership
            for membership in self.memberships.values()
            if membership.user_id == user_id
        ]

    async def get_membership(
        self,
        offering_id: UUID,
        user_id: UUID,
    ) -> CourseMembership:
        if user_id not in self.existing_profile_ids:
            raise ProfileNotFoundError

        if offering_id not in self.existing_offering_ids:
            raise OfferingNotFoundError

        membership = self.memberships.get((user_id, offering_id))

        if membership is None:
            raise MembershipNotFoundError

        return membership

    async def update_membership_status(
        self,
        offering_id: UUID,
        user_id: UUID,
        new_status: MembershipStatus,
    ) -> CourseMembership:
        if user_id not in self.existing_profile_ids:
            raise ProfileNotFoundError

        if offering_id not in self.existing_offering_ids:
            raise OfferingNotFoundError

        membership = self.memberships.get((user_id, offering_id))

        if membership is None:
            raise MembershipNotFoundError

        allowed_terminal_statuses = {
            MembershipStatus.COMPLETED,
            MembershipStatus.WITHDRAWN,
            MembershipStatus.REMOVED,
        }

        if (
            membership.status != MembershipStatus.ACTIVE
            or new_status not in allowed_terminal_statuses
        ):
            raise InvalidMembershipTransitionError

        membership.status = new_status
        membership.ended_at = datetime.now(UTC)

        return membership


def authenticated_user(user_id: UUID):
    async def _get_current_user() -> AuthenticatedUser:
        return AuthenticatedUser(user_id=user_id)

    return _get_current_user


@pytest.fixture
def fake_service() -> FakeMembershipService:
    return FakeMembershipService()


@pytest.fixture
def app(fake_service: FakeMembershipService) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(router)

    test_app.dependency_overrides[get_membership_service] = lambda: fake_service
    test_app.dependency_overrides[get_current_user] = authenticated_user(TEST_USER_ID)

    return test_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_create_membership(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert response.status_code == 201

    body = response.json()

    assert body["user_id"] == str(TEST_USER_ID)
    assert body["offering_id"] == str(offering_id)
    assert body["status"] == MembershipStatus.ACTIVE.value
    assert body["ended_at"] is None


def test_create_membership_uses_authenticated_user(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == str(TEST_USER_ID)


def test_create_membership_profile_not_found(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_offering_ids.add(offering_id)

    response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_create_membership_offering_not_found(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)

    response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Offering not found"


def test_create_duplicate_membership(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    first_response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    second_response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Membership already exists"


def test_list_offering_memberships(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()
    second_user_id = uuid4()

    fake_service.existing_offering_ids.add(offering_id)
    fake_service.existing_profile_ids.update(
        {
            TEST_USER_ID,
            second_user_id,
        }
    )

    awaitable_membership_one = CourseMembership(
        user_id=TEST_USER_ID,
        offering_id=offering_id,
        status=MembershipStatus.ACTIVE,
        joined_at=datetime.now(UTC),
        ended_at=None,
    )

    awaitable_membership_two = CourseMembership(
        user_id=second_user_id,
        offering_id=offering_id,
        status=MembershipStatus.ACTIVE,
        joined_at=datetime.now(UTC),
        ended_at=None,
    )

    fake_service.memberships[(TEST_USER_ID, offering_id)] = awaitable_membership_one
    fake_service.memberships[(second_user_id, offering_id)] = awaitable_membership_two

    response = client.get(
        f"/offerings/{offering_id}/memberships",
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert {membership["user_id"] for membership in body} == {
        str(TEST_USER_ID),
        str(second_user_id),
    }


def test_list_empty_offering_memberships(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_offering_ids.add(offering_id)

    response = client.get(
        f"/offerings/{offering_id}/memberships",
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_nonexistent_offering_memberships(
    client: TestClient,
):
    offering_id = uuid4()

    response = client.get(
        f"/offerings/{offering_id}/memberships",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Offering not found"


def test_list_user_memberships(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    first_offering_id = uuid4()
    second_offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.update(
        {
            first_offering_id,
            second_offering_id,
        }
    )

    fake_service.memberships[(TEST_USER_ID, first_offering_id)] = CourseMembership(
        user_id=TEST_USER_ID,
        offering_id=first_offering_id,
        status=MembershipStatus.ACTIVE,
        joined_at=datetime.now(UTC),
        ended_at=None,
    )

    fake_service.memberships[(TEST_USER_ID, second_offering_id)] = CourseMembership(
        user_id=TEST_USER_ID,
        offering_id=second_offering_id,
        status=MembershipStatus.ACTIVE,
        joined_at=datetime.now(UTC),
        ended_at=None,
    )

    response = client.get("/users/me/memberships")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert {membership["offering_id"] for membership in body} == {
        str(first_offering_id),
        str(second_offering_id),
    }


def test_list_empty_user_memberships(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    fake_service.existing_profile_ids.add(TEST_USER_ID)

    response = client.get("/users/me/memberships")

    assert response.status_code == 200
    assert response.json() == []


def test_list_nonexistent_user_memberships(
    app: FastAPI,
    fake_service: FakeMembershipService,
):
    app.dependency_overrides[get_current_user] = authenticated_user(MISSING_USER_ID)

    client = TestClient(app)

    response = client.get("/users/me/memberships")

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_get_membership(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    fake_service.memberships[(TEST_USER_ID, offering_id)] = CourseMembership(
        user_id=TEST_USER_ID,
        offering_id=offering_id,
        status=MembershipStatus.ACTIVE,
        joined_at=datetime.now(UTC),
        ended_at=None,
    )

    response = client.get(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == str(TEST_USER_ID)
    assert body["offering_id"] == str(offering_id)
    assert body["status"] == MembershipStatus.ACTIVE.value


def test_get_nonexistent_membership(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    response = client.get(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Membership not found"


def test_update_membership_status(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    create_response = client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    assert create_response.status_code == 201

    response = client.patch(
        f"/offerings/{offering_id}/memberships/me",
        json={"status": MembershipStatus.COMPLETED.value},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == str(TEST_USER_ID)
    assert body["offering_id"] == str(offering_id)
    assert body["status"] == MembershipStatus.COMPLETED.value
    assert body["ended_at"] is not None


def test_update_membership_active_to_active_rejected(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    response = client.patch(
        f"/offerings/{offering_id}/memberships/me",
        json={"status": MembershipStatus.ACTIVE.value},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Invalid membership status transition")


def test_update_terminal_membership_rejected(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    client.post(
        f"/offerings/{offering_id}/memberships/me",
    )

    first_response = client.patch(
        f"/offerings/{offering_id}/memberships/me",
        json={"status": MembershipStatus.COMPLETED.value},
    )

    assert first_response.status_code == 200

    second_response = client.patch(
        f"/offerings/{offering_id}/memberships/me",
        json={"status": MembershipStatus.WITHDRAWN.value},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == ("Invalid membership status transition")


def test_update_nonexistent_membership(
    client: TestClient,
    fake_service: FakeMembershipService,
):
    offering_id = uuid4()

    fake_service.existing_profile_ids.add(TEST_USER_ID)
    fake_service.existing_offering_ids.add(offering_id)

    response = client.patch(
        f"/offerings/{offering_id}/memberships/me",
        json={"status": MembershipStatus.WITHDRAWN.value},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Membership not found"

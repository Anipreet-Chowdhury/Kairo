from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from app.api.routes.profiles import get_profile_service, router
from app.core.exceptions import ProfileAlreadyExistsError, ProfileNotFoundError
from app.core.security import get_current_user
from app.db.models.enums import ProfileRole
from app.schemas.auth import AuthenticatedUser
from app.schemas.profile import ProfileCreate
from fastapi import FastAPI
from fastapi.testclient import TestClient

TEST_USER_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeProfile:
    def __init__(
        self,
        user_id: UUID,
        display_name: str,
        role: ProfileRole,
    ):
        self.user_id = user_id
        self.display_name = display_name
        self.role = role
        self.created_at = datetime.now(UTC)


class FakeProfileService:
    def __init__(self):
        self.profiles: dict[UUID, FakeProfile] = {}

    async def create_profile(
        self,
        user_id: UUID,
        data: ProfileCreate,
    ) -> FakeProfile:
        if user_id in self.profiles:
            raise ProfileAlreadyExistsError

        profile = FakeProfile(
            user_id=user_id,
            display_name=data.display_name,
            role=data.role,
        )
        self.profiles[user_id] = profile

        return profile

    async def get_profile(
        self,
        user_id: UUID,
    ) -> FakeProfile:
        profile = self.profiles.get(user_id)

        if profile is None:
            raise ProfileNotFoundError

        return profile


@pytest.fixture
def fake_service() -> FakeProfileService:
    return FakeProfileService()


@pytest.fixture
def client(fake_service: FakeProfileService) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    async def fake_current_user() -> AuthenticatedUser:
        return AuthenticatedUser(user_id=TEST_USER_ID)

    app.dependency_overrides[get_profile_service] = lambda: fake_service
    app.dependency_overrides[get_current_user] = fake_current_user

    return TestClient(app)


def test_create_profile(
    client: TestClient,
):
    response = client.post(
        "/profiles/me",
        json={
            "display_name": "Test Student",
            "role": "student",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["user_id"] == str(TEST_USER_ID)
    assert body["display_name"] == "Test Student"
    assert body["role"] == "student"
    assert "created_at" in body


def test_create_duplicate_profile_returns_409(
    client: TestClient,
):
    data = {
        "display_name": "Test Student",
        "role": "student",
    }

    first_response = client.post("/profiles/me", json=data)
    second_response = client.post("/profiles/me", json=data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Profile already exists"


def test_get_profile(
    client: TestClient,
):
    client.post(
        "/profiles/me",
        json={
            "display_name": "Test Student",
            "role": "student",
        },
    )

    response = client.get("/profiles/me")

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == str(TEST_USER_ID)
    assert body["display_name"] == "Test Student"
    assert body["role"] == "student"


def test_get_missing_profile_returns_404(
    client: TestClient,
):
    response = client.get("/profiles/me")

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_profile_user_id_comes_from_authenticated_user(
    client: TestClient,
):
    random_other_user = uuid4()

    response = client.post(
        "/profiles/me",
        json={
            "display_name": "Test Student",
            "role": "student",
            "user_id": str(random_other_user),
        },
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == str(TEST_USER_ID)

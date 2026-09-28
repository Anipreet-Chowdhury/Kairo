from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from app.api.routes.offerings import get_offering_service
from app.core.exceptions import (
    CourseNotFoundError,
    OfferingAlreadyExistsError,
    OfferingNotFoundError,
)
from app.db.models.course_offering import CourseOffering
from app.main import app
from app.schemas.offerings import OfferingCreate
from fastapi.testclient import TestClient


class FakeOfferingService:
    def __init__(self) -> None:
        self.offerings: dict[UUID, CourseOffering] = {}
        self.existing_course_ids: set[UUID] = set()

    async def create_offering(
        self,
        course_id: UUID,
        data: OfferingCreate,
    ) -> CourseOffering:
        if course_id not in self.existing_course_ids:
            raise CourseNotFoundError

        duplicate = any(
            offering.course_id == course_id
            and offering.term == data.term
            and offering.year == data.year
            for offering in self.offerings.values()
        )

        if duplicate:
            raise OfferingAlreadyExistsError

        offering = CourseOffering(
            offering_id=uuid4(),
            course_id=course_id,
            term=data.term,
            year=data.year,
            created_at=datetime.now(UTC),
        )

        self.offerings[offering.offering_id] = offering
        return offering

    async def list_course_offerings(
        self,
        course_id: UUID,
    ) -> list[CourseOffering]:
        if course_id not in self.existing_course_ids:
            raise CourseNotFoundError

        return [
            offering
            for offering in self.offerings.values()
            if offering.course_id == course_id
        ]

    async def get_offering(
        self,
        offering_id: UUID,
    ) -> CourseOffering:
        offering = self.offerings.get(offering_id)

        if offering is None:
            raise OfferingNotFoundError

        return offering


@pytest.fixture
def fake_service() -> FakeOfferingService:
    return FakeOfferingService()


@pytest.fixture
def client(fake_service: FakeOfferingService):
    app.dependency_overrides[get_offering_service] = lambda: fake_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_offering(
    client: TestClient,
    fake_service: FakeOfferingService,
) -> None:
    course_id = uuid4()
    fake_service.existing_course_ids.add(course_id)

    response = client.post(
        f"/courses/{course_id}/offerings",
        json={
            "term": "fall",
            "year": 2026,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["course_id"] == str(course_id)
    assert body["term"] == "fall"
    assert body["year"] == 2026
    assert "offering_id" in body
    assert "created_at" in body


def test_create_offering_for_nonexistent_course_returns_404(
    client: TestClient,
) -> None:
    course_id = uuid4()

    response = client.post(
        f"/courses/{course_id}/offerings",
        json={
            "term": "fall",
            "year": 2026,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_duplicate_offering_returns_409(
    client: TestClient,
    fake_service: FakeOfferingService,
) -> None:
    course_id = uuid4()
    fake_service.existing_course_ids.add(course_id)

    payload = {
        "term": "fall",
        "year": 2026,
    }

    first_response = client.post(
        f"/courses/{course_id}/offerings",
        json=payload,
    )
    second_response = client.post(
        f"/courses/{course_id}/offerings",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Offering already exists"


def test_list_course_offerings(
    client: TestClient,
    fake_service: FakeOfferingService,
) -> None:
    course_id = uuid4()
    fake_service.existing_course_ids.add(course_id)

    client.post(
        f"/courses/{course_id}/offerings",
        json={
            "term": "fall",
            "year": 2026,
        },
    )

    response = client.get(f"/courses/{course_id}/offerings")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["course_id"] == str(course_id)
    assert body[0]["term"] == "fall"
    assert body[0]["year"] == 2026


def test_list_course_with_no_offerings_returns_empty_list(
    client: TestClient,
    fake_service: FakeOfferingService,
) -> None:
    course_id = uuid4()
    fake_service.existing_course_ids.add(course_id)

    response = client.get(f"/courses/{course_id}/offerings")

    assert response.status_code == 200
    assert response.json() == []


def test_list_nonexistent_course_returns_404(
    client: TestClient,
) -> None:
    response = client.get(f"/courses/{uuid4()}/offerings")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_get_offering(
    client: TestClient,
    fake_service: FakeOfferingService,
) -> None:
    course_id = uuid4()
    fake_service.existing_course_ids.add(course_id)

    create_response = client.post(
        f"/courses/{course_id}/offerings",
        json={
            "term": "winter",
            "year": 2027,
        },
    )

    offering_id = create_response.json()["offering_id"]

    response = client.get(f"/offerings/{offering_id}")

    assert response.status_code == 200

    body = response.json()

    assert body["offering_id"] == offering_id
    assert body["course_id"] == str(course_id)
    assert body["term"] == "winter"
    assert body["year"] == 2027


def test_get_nonexistent_offering_returns_404(
    client: TestClient,
) -> None:
    response = client.get(f"/offerings/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Offering not found"

from datetime import UTC, datetime
from uuid import uuid4

from app.api.routes.courses import get_course_service
from app.db.models.courses import Course
from app.main import app
from fastapi.testclient import TestClient


class FakeCourseService:
    def __init__(self):
        self.courses = {}

    async def create_course(self, data):
        course = Course(
            course_id=uuid4(),
            course_code=data.course_code,
            course_name=data.course_name,
            collaboration_type=data.collaboration_type,
            created_at=datetime.now(UTC),
        )

        self.courses[course.course_id] = course
        return course

    async def list_courses(self):
        return list(self.courses.values())

    async def get_course(self, course_id):
        course = self.courses.get(course_id)

        if course is None:
            raise ValueError("Course not found")

        return course


fake_service = FakeCourseService()


def override_get_course_service():
    return fake_service


app.dependency_overrides[get_course_service] = override_get_course_service

client = TestClient(app)


def test_create_course():
    response = client.post(
        "/courses",
        json={
            "course_code": "ECE421",
            "course_name": "Introduction to Machine Learning",
            "collaboration_type": "individual",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["course_code"] == "ECE421"
    assert body["course_name"] == "Introduction to Machine Learning"
    assert body["collaboration_type"] == "individual"
    assert "course_id" in body
    assert "created_at" in body


def test_list_courses():
    response = client.get("/courses")

    assert response.status_code == 200

    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1


def test_get_existing_course():
    course_id = next(iter(fake_service.courses))

    response = client.get(f"/courses/{course_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["course_id"] == str(course_id)
    assert body["course_code"] == "ECE421"


def test_get_nonexistent_course():
    nonexistent_id = uuid4()

    response = client.get(f"/courses/{nonexistent_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Course not found"}

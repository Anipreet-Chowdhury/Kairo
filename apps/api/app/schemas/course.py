from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import CollaborationType


class CourseCreate(BaseModel):
    course_code: str = Field(
        ..., min_length=1, max_length=20, description="Code for the course"
    )
    course_name: str = Field(
        ..., min_length=1, max_length=255, description="Full name for the course"
    )
    collaboration_type: CollaborationType


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: UUID
    course_code: str
    course_name: str
    collaboration_type: CollaborationType
    created_at: datetime

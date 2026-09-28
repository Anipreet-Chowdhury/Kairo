from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import TermType


class OfferingCreate(BaseModel):
    term: TermType
    year: int = Field(
        ..., ge=2000, le=2100, description="Year in which the course was offered"
    )


class OfferingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offering_id: UUID
    course_id: UUID
    term: TermType
    year: int
    created_at: datetime

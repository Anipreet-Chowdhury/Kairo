from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import MembershipStatus


class MembershipCreate(BaseModel):
    user_id: UUID


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    offering_id: UUID
    status: MembershipStatus
    joined_at: datetime
    ended_at: datetime | None


class MembershipUpdate(BaseModel):
    status: MembershipStatus

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import ProfileRole


class ProfileCreate(BaseModel):
    display_name: str = Field(
        ..., min_length=1, max_length=255, description="The display name of the profile"
    )
    role: ProfileRole


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    display_name: str
    role: ProfileRole
    created_at: datetime

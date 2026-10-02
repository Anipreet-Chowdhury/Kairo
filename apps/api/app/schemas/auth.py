from uuid import UUID

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: UUID

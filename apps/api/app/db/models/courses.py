from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import CollaborationType


class Course(Base):
    __tablename__ = "courses"

    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    course_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    course_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    collaboration_type: Mapped[CollaborationType] = mapped_column(
        Enum(
            CollaborationType,
            name="collaboration_type",
            values_callable=lambda enum_class: [e.value for e in enum_class],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

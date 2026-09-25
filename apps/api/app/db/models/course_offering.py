from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import TermType


class CourseOffering(Base):
    __tablename__ = "course_offerings"

    offering_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("courses.course_id"),
        nullable=False,
    )
    term: Mapped[TermType] = mapped_column(
        Enum(
            TermType,
            name="term_type",
            values_callable=lambda enum_class: [e.value for e in enum_class],
        ),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint(
            "course_id", "term", "year", name="unique_course_offerings_course_term_year"
        ),
    )

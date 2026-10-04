from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import AssessmentType, CollaborationType


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    offering_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("course_offerings.offering_id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    assessment_type: Mapped[AssessmentType] = mapped_column(
        Enum(
            AssessmentType,
            name="assessment_type",
            values_callable=lambda enum_class: [e.value for e in enum_class],
        ),
        nullable=False,
    )
    assessment_type_label: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    collaboration_type: Mapped[CollaborationType] = mapped_column(
        Enum(
            CollaborationType,
            name="collaboration_type",
            values_callable=lambda enum_class: [e.value for e in enum_class],
        ),
        nullable=False,
    )
    weight: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "weight IS NULL OR (weight >= 0 AND weight <= 100)",
            name="ck_assessments_weight_range",
        ),
        CheckConstraint(
            "ends_at IS NULL OR starts_at IS NOT NULL",
            name="ck_assessments_end_requires_start",
        ),
        CheckConstraint(
            "ends_at IS NULL OR ends_at > starts_at",
            name="ck_assessments_end_after_start",
        ),
    )

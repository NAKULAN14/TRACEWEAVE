"""
TRACEWEAVE - Investigation Database Model
"""

from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String

from backend.app.database import Base


class Investigation(Base):

    __tablename__ = "investigations"

    investigation_id = Column(
        String(64),
        primary_key=True,
        index=True,
    )

    case_id = Column(
        String(64),
        ForeignKey("cases.case_id"),
        nullable=False,
        index=True,
    )

    status = Column(
        String(32),
        nullable=False,
        default="PENDING",
    )

    current_stage = Column(
        String(64),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message = Column(
        String(2000),
        nullable=True,
    )
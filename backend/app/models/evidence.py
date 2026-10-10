"""
TRACEWEAVE - Evidence Database Model
"""

from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from backend.app.database import Base


class Evidence(Base):

    __tablename__ = "evidence"

    evidence_id = Column(
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

    original_filename = Column(
        String(255),
        nullable=False,
    )

    stored_filename = Column(
        String(255),
        nullable=False,
    )

    storage_path = Column(
        String(1000),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    sha256 = Column(
        String(64),
        nullable=False,
        index=True,
    )

    mime_type = Column(
        String(255),
        nullable=True,
    )

    extension = Column(
        String(32),
        nullable=True,
    )

    imported_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    status = Column(
        String(32),
        nullable=False,
        default="IMPORTED",
    )
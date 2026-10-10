"""
TRACEWEAVE - Investigation Service

Coordinates the lifecycle of a TRACEWEAVE investigation.
The service orchestrates existing forensic modules
rather than duplicating their functionality.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.case import Case
from backend.app.models.investigation import Investigation


SUPPORTED_STATUSES = {
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
}


def create_investigation(
    db: Session,
    case_id: str,
) -> Investigation:
    """
    Create a new investigation for an existing case.
    """

    case = (
        db.query(Case)
        .filter(
            Case.case_id == case_id
        )
        .first()
    )

    if case is None:
        raise ValueError(
            "Case not found."
        )

    investigation_id = (
        f"INV-{uuid4().hex[:12].upper()}"
    )

    investigation = Investigation(
        investigation_id=investigation_id,
        case_id=case_id,
        status="PENDING",
        current_stage=None,
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return investigation


def start_investigation(
    db: Session,
    investigation: Investigation,
) -> Investigation:
    """
    Move an investigation from PENDING to RUNNING.
    """

    if investigation.status != "PENDING":
        raise ValueError(
            "Only PENDING investigations "
            "can be started."
        )

    investigation.status = "RUNNING"

    investigation.started_at = (
        datetime.now(timezone.utc)
    )

    investigation.current_stage = (
        "INGESTION"
    )

    db.commit()
    db.refresh(investigation)

    return investigation


def update_investigation_stage(
    db: Session,
    investigation: Investigation,
    stage: str,
) -> Investigation:
    """
    Update the current investigation stage.
    """

    if investigation.status != "RUNNING":
        raise ValueError(
            "Only RUNNING investigations "
            "can update stages."
        )

    if not stage:
        raise ValueError(
            "Investigation stage is required."
        )

    investigation.current_stage = stage

    db.commit()
    db.refresh(investigation)

    return investigation


def complete_investigation(
    db: Session,
    investigation: Investigation,
) -> Investigation:
    """
    Mark an investigation as completed.
    """

    if investigation.status != "RUNNING":
        raise ValueError(
            "Only RUNNING investigations "
            "can be completed."
        )

    investigation.status = "COMPLETED"

    investigation.current_stage = (
        "COMPLETED"
    )

    investigation.completed_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(investigation)

    return investigation


def fail_investigation(
    db: Session,
    investigation: Investigation,
    error_message: str,
) -> Investigation:
    """
    Mark an investigation as failed.
    """

    if investigation.status != "RUNNING":
        raise ValueError(
            "Only RUNNING investigations "
            "can fail."
        )

    if not error_message:
        raise ValueError(
            "error_message is required."
        )

    investigation.status = "FAILED"

    investigation.error_message = (
        error_message
    )

    investigation.completed_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(investigation)

    return investigation


def validate_investigation(
    investigation: Investigation,
) -> None:
    """
    Validate the investigation lifecycle state.
    """

    if investigation.status not in (
        SUPPORTED_STATUSES
    ):
        raise ValueError(
            f"Unsupported investigation status: "
            f"{investigation.status}"
        )

    if not investigation.investigation_id:
        raise ValueError(
            "Missing investigation ID."
        )

    if not investigation.case_id:
        raise ValueError(
            "Missing case ID."
        )

    if investigation.status == "RUNNING":

        if investigation.started_at is None:
            raise ValueError(
                "RUNNING investigation must "
                "have started_at."
            )

        if not investigation.current_stage:
            raise ValueError(
                "RUNNING investigation must "
                "have a current stage."
            )

    if investigation.status in (
        "COMPLETED",
        "FAILED",
    ):

        if investigation.completed_at is None:
            raise ValueError(
                "Finished investigation must "
                "have completed_at."
            )


if __name__ == "__main__":

    print(
        "INVESTIGATION SERVICE: READY"
    )
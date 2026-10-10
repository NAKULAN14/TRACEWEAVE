"""
TRACEWEAVE - Investigation API
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.case import Case
from backend.app.models.investigation import Investigation
from backend.app.schemas.investigation import (
    InvestigationResponse,
)
from backend.app.services.investigation_service import (
    create_investigation,
    start_investigation,
    validate_investigation,
)
from backend.app.schemas.investigation_status import (
    InvestigationStageStatus,
    InvestigationStatusResponse,
)

from backend.app.services.investigation_status import (
    build_stage_status,
)

router = APIRouter(
    tags=["Investigations"],
)


@router.post(
    "/api/cases/{case_id}/investigations",
    response_model=InvestigationResponse,
    status_code=201,
)
def create_case_investigation(
    case_id: str,
    db: Session = Depends(get_db),
):
    """
    Create a new investigation for a case.
    """

    try:

        investigation = create_investigation(
            db,
            case_id,
        )

        validate_investigation(
            investigation
        )

        return investigation

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/api/cases/{case_id}/investigations",
    response_model=list[InvestigationResponse],
)
def list_case_investigations(
    case_id: str,
    db: Session = Depends(get_db),
):
    """
    List investigations belonging to a case.
    """

    case = (
        db.query(Case)
        .filter(
            Case.case_id == case_id
        )
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    return (
        db.query(Investigation)
        .filter(
            Investigation.case_id == case_id
        )
        .order_by(
            Investigation.created_at.desc()
        )
        .all()
    )


@router.get(
    "/api/investigations/{investigation_id}",
    response_model=InvestigationResponse,
)
def get_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve one investigation.
    """

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id
            == investigation_id
        )
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return investigation


@router.post(
    "/api/investigations/{investigation_id}/start",
    response_model=InvestigationResponse,
)
def start_case_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    """
    Start a pending investigation.
    """

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id
            == investigation_id
        )
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    try:

        investigation = start_investigation(
            db,
            investigation,
        )

        validate_investigation(
            investigation
        )

        return investigation

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
@router.get(
    "/api/investigations/{investigation_id}/status",
    response_model=InvestigationStatusResponse,
)
def get_investigation_status(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    """
    Return current investigation status and
    all pipeline stages.
    """

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id
            == investigation_id
        )
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    stages = build_stage_status(
        investigation
    )

    return {
        "investigation_id":
            investigation.investigation_id,

        "case_id":
            investigation.case_id,

        "status":
            investigation.status,

        "current_stage":
            investigation.current_stage,

        "stages":
            stages,
    }


@router.get(
    "/api/investigations/{investigation_id}/stages",
    response_model=list[InvestigationStageStatus],
)
def get_investigation_stages(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the status of every investigation stage.
    """

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id
            == investigation_id
        )
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return build_stage_status(
        investigation
    )
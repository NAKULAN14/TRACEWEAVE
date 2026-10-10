"""
TRACEWEAVE - Case Management API
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.case import Case
from backend.app.schemas.case import CaseCreate
from backend.app.schemas.case import CaseResponse
from backend.app.schemas.case import CaseUpdate


router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"],
)


SUPPORTED_STATUSES = {
    "OPEN",
    "UNDER_INVESTIGATION",
    "RECONSTRUCTED",
    "CLOSED",
}


@router.post(
    "",
    response_model=CaseResponse,
    status_code=201,
)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
):

    case_id = (
        f"CASE-{uuid4().hex[:12].upper()}"
    )

    case = Case(
        case_id=case_id,
        title=case_data.title,
        description=case_data.description,
        status="OPEN",
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


@router.get(
    "",
    response_model=list[CaseResponse],
)
def list_cases(
    db: Session = Depends(get_db),
):

    return (
        db.query(Case)
        .order_by(Case.created_at.desc())
        .all()
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):

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

    return case


@router.put(
    "/{case_id}",
    response_model=CaseResponse,
)
def update_case(
    case_id: str,
    case_data: CaseUpdate,
    db: Session = Depends(get_db),
):

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

    if case_data.status is not None:

        if (
            case_data.status
            not in SUPPORTED_STATUSES
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported case status."
                ),
            )

        case.status = case_data.status

    if case_data.title is not None:
        case.title = case_data.title

    if case_data.description is not None:
        case.description = (
            case_data.description
        )

    case.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(case)

    return case
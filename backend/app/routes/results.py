
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.results import InvestigationResultResponse
from backend.app.services.results_service import (
    SUPPORTED_RESULT_TYPES,
    get_investigation_result,
)


router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigation Results"],
)


@router.get(
    "/{investigation_id}/results/{result_type}",
    response_model=InvestigationResultResponse,
)
def read_investigation_result(
    investigation_id: str,
    result_type: str,
    db: Session = Depends(get_db),
):
    if result_type not in SUPPORTED_RESULT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported result type. Choose from: "
                   f"{', '.join(sorted(SUPPORTED_RESULT_TYPES))}",
        )

    result = get_investigation_result(db, investigation_id, result_type)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result


@router.get("/{investigation_id}/results")
def list_investigation_result_types(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    from backend.app.models.investigation import Investigation

    investigation = (
        db.query(Investigation)
        .filter(Investigation.investigation_id == investigation_id)
        .first()
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "available_result_types": sorted(SUPPORTED_RESULT_TYPES),
        "status": "NOT_AVAILABLE",
        "message": "Result types are registered; analysis output is not connected yet.",
    }

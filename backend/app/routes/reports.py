
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.report import InvestigationReportResponse
from backend.app.services.report_service import get_investigation_report


router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigation Reports"],
)


@router.get(
    "/{investigation_id}/report",
    response_model=InvestigationReportResponse,
)
def read_investigation_report(
    investigation_id: str,
    report_format: str = Query(
        default="json",
        pattern="^(json|html|markdown)$",
    ),
    db: Session = Depends(get_db),
):
    try:
        result = get_investigation_report(
            db,
            investigation_id,
            report_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.risk import RiskAssessmentResponse
from backend.app.schemas.recommendations import RecommendationsResponse
from backend.app.services.risk_recommendation_service import (
    get_risk_assessment,
    get_recommendations,
)


router = APIRouter(
    prefix="/api/investigations",
    tags=["Risk and Recommendations"],
)


@router.get(
    "/{investigation_id}/risk",
    response_model=RiskAssessmentResponse,
)
def read_risk_assessment(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    result = get_risk_assessment(db, investigation_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result


@router.get(
    "/{investigation_id}/recommendations",
    response_model=RecommendationsResponse,
)
def read_recommendations(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    result = get_recommendations(db, investigation_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result

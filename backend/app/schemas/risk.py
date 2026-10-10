
from typing import Any
from pydantic import BaseModel, ConfigDict


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    case_id: str
    status: str
    overall_risk: str | None = None
    risk_score: float | None = None
    factors: list[dict[str, Any]] = []
    message: str | None = None

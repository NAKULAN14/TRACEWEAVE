
from typing import Any
from pydantic import BaseModel, ConfigDict


class RecommendationsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    case_id: str
    status: str
    recommendations: list[dict[str, Any]] = []
    message: str | None = None

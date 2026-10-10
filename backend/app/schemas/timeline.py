from typing import Any
from pydantic import BaseModel, ConfigDict


class TimelineResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    case_id: str
    status: str
    events: list[dict[str, Any]] = []
    message: str | None = None

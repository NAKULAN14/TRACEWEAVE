
from pydantic import BaseModel, ConfigDict
from typing import Any


class InvestigationResultResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    case_id: str
    result_type: str
    status: str
    data: Any = None
    message: str | None = None

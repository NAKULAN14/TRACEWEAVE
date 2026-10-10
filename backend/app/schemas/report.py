
from pydantic import BaseModel, ConfigDict


class InvestigationReportResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    investigation_id: str
    case_id: str
    status: str
    report_format: str
    report_content: str | None = None
    message: str | None = None

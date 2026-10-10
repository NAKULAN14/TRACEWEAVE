"""
TRACEWEAVE - Investigation API Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class InvestigationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    investigation_id: str
    case_id: str
    status: str
    current_stage: Optional[str]

    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    error_message: Optional[str]
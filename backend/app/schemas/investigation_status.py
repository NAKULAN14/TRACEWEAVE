"""
TRACEWEAVE - Investigation Status Schemas
"""

from typing import List, Optional

from pydantic import BaseModel


class InvestigationStageStatus(BaseModel):

    sequence: int
    stage: str
    status: str


class InvestigationStatusResponse(BaseModel):

    investigation_id: str
    case_id: str
    status: str
    current_stage: Optional[str]

    stages: List[
        InvestigationStageStatus
    ]
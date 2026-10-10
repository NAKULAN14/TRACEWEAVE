"""
TRACEWEAVE - Case API Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class CaseCreate(BaseModel):

    title: str
    description: Optional[str] = None


class CaseUpdate(BaseModel):

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CaseResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    case_id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
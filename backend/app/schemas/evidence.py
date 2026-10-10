"""
TRACEWEAVE - Evidence API Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class EvidenceResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    evidence_id: str
    case_id: str

    original_filename: str
    stored_filename: str
    storage_path: str

    file_size: int
    sha256: str

    mime_type: Optional[str]
    extension: Optional[str]

    imported_at: datetime
    status: str
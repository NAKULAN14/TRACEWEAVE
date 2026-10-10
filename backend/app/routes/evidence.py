"""
TRACEWEAVE - Evidence Upload API
"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.case import Case
from backend.app.models.evidence import Evidence
from backend.app.schemas.evidence import EvidenceResponse
from backend.app.services.evidence_storage import (
    save_uploaded_evidence,
)
from backend.app.services.evidence_ingestion import (
    ingest_stored_evidence,
)


router = APIRouter(
    prefix="/api/cases/{case_id}/evidence",
    tags=["Evidence"],
)


@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=201,
)
async def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------
    # 1. Verify case exists
    # --------------------------------------------------

    case = (
        db.query(Case)
        .filter(
            Case.case_id == case_id
        )
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    # --------------------------------------------------
    # 2. Save original evidence
    # --------------------------------------------------

    try:

        (
            stored_filename,
            storage_path,
            file_size,
        ) = await save_uploaded_evidence(
            file,
            case_id,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to store evidence: "
                f"{exc}"
            ),
        ) from exc

    # --------------------------------------------------
    # 3. Run existing forensic ingestion engine
    # --------------------------------------------------

    try:

        ingestion_result = (
            ingest_stored_evidence(
                storage_path
            )
        )

    except Exception as exc:

        # Do not delete the stored original.
        # It remains available for forensic review.

        raise HTTPException(
            status_code=500,
            detail=(
                "Evidence ingestion failed: "
                f"{exc}"
            ),
        ) from exc

    # --------------------------------------------------
    # 4. Create database evidence record
    # --------------------------------------------------

    evidence_id = (
        f"EVID-{uuid4().hex[:12].upper()}"
    )

    evidence = Evidence(
        evidence_id=evidence_id,
        case_id=case_id,
        original_filename=(
            file.filename
        ),
        stored_filename=stored_filename,
        storage_path=str(
            Path(storage_path)
        ),
        file_size=ingestion_result[
            "size_bytes"
        ],
        sha256=ingestion_result[
            "sha256"
        ],
        mime_type=ingestion_result.get(
            "mime_type"
        ),
        extension=ingestion_result.get(
            "extension"
        ),
        imported_at=ingestion_result[
            "imported_at"
        ],
        status="IMPORTED",
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


# ======================================================
# 22.3.6 — Evidence Retrieval
# ======================================================

@router.get(
    "",
    response_model=list[EvidenceResponse],
)
def list_evidence(
    case_id: str,
    db: Session = Depends(get_db),
):
    """
    List all evidence associated with a case.
    """

    case = (
        db.query(Case)
        .filter(
            Case.case_id == case_id
        )
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found.",
        )

    return (
        db.query(Evidence)
        .filter(
            Evidence.case_id == case_id
        )
        .order_by(
            Evidence.imported_at.desc()
        )
        .all()
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_evidence(
    case_id: str,
    evidence_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve metadata for one evidence item.
    """

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.case_id == case_id,
            Evidence.evidence_id == evidence_id,
        )
        .first()
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    return evidence
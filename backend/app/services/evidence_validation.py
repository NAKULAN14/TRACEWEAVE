"""
TRACEWEAVE - Evidence API Validation
"""

from pathlib import Path

from backend.app.config import EVIDENCE_ROOT
from backend.app.database import SessionLocal
from backend.app.models.case import Case
from backend.app.models.evidence import Evidence


def validate_evidence_records():
    db = SessionLocal()

    try:
        cases = db.query(Case).all()

        if not cases:
            raise ValueError(
                "No cases found. Create a test case first."
            )

        evidence_records = (
            db.query(Evidence).all()
        )

        if not evidence_records:
            raise ValueError(
                "No evidence records found. "
                "Upload evidence first."
            )

        for evidence in evidence_records:

            # ------------------------------------------
            # 1. Required fields
            # ------------------------------------------

            required_fields = [
                "evidence_id",
                "case_id",
                "original_filename",
                "stored_filename",
                "storage_path",
                "file_size",
                "sha256",
                "imported_at",
                "status",
            ]

            for field in required_fields:

                if getattr(
                    evidence,
                    field,
                ) is None:

                    raise ValueError(
                        f"Missing field '{field}' "
                        f"for {evidence.evidence_id}"
                    )

            # ------------------------------------------
            # 2. Case relationship
            # ------------------------------------------

            case = (
                db.query(Case)
                .filter(
                    Case.case_id
                    == evidence.case_id
                )
                .first()
            )

            if case is None:
                raise ValueError(
                    f"Evidence {evidence.evidence_id} "
                    f"references a nonexistent case."
                )

            # ------------------------------------------
            # 3. SHA-256 validation
            # ------------------------------------------

            if len(evidence.sha256) != 64:
                raise ValueError(
                    f"Invalid SHA-256 length for "
                    f"{evidence.evidence_id}"
                )

            try:
                int(
                    evidence.sha256,
                    16,
                )
            except ValueError as exc:
                raise ValueError(
                    f"Invalid SHA-256 value for "
                    f"{evidence.evidence_id}"
                ) from exc

            # ------------------------------------------
            # 4. Stored file exists
            # ------------------------------------------

            storage_path = Path(
                evidence.storage_path
            )

            if not storage_path.exists():
                raise ValueError(
                    f"Stored evidence file missing: "
                    f"{storage_path}"
                )

            if not storage_path.is_file():
                raise ValueError(
                    f"Evidence path is not a file: "
                    f"{storage_path}"
                )

            # ------------------------------------------
            # 5. File size validation
            # ------------------------------------------

            actual_size = (
                storage_path.stat().st_size
            )

            if actual_size != evidence.file_size:
                raise ValueError(
                    f"File size mismatch for "
                    f"{evidence.evidence_id}: "
                    f"database={evidence.file_size}, "
                    f"actual={actual_size}"
                )

            # ------------------------------------------
            # 6. Storage location validation
            # ------------------------------------------

            try:
                storage_path.resolve().relative_to(
                    EVIDENCE_ROOT.resolve()
                )
            except ValueError as exc:
                raise ValueError(
                    f"Evidence file is outside "
                    f"the controlled evidence "
                    f"storage directory: "
                    f"{storage_path}"
                ) from exc

            # ------------------------------------------
            # 7. Status validation
            # ------------------------------------------

            if evidence.status != "IMPORTED":
                raise ValueError(
                    f"Unexpected evidence status "
                    f"for {evidence.evidence_id}: "
                    f"{evidence.status}"
                )

        return {
            "cases": len(cases),
            "evidence_records": len(
                evidence_records
            ),
        }

    finally:
        db.close()


if __name__ == "__main__":

    result = validate_evidence_records()

    print(
        "EVIDENCE API VALIDATION: PASS"
    )

    print(
        "Cases:",
        result["cases"],
    )

    print(
        "Evidence records:",
        result["evidence_records"],
    )
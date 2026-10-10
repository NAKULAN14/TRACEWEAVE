"""
TRACEWEAVE - Backend Evidence Ingestion Adapter

Connects the FastAPI backend to the existing
TRACEWEAVE forensic evidence ingestion engine.
"""

from pathlib import Path
from typing import Any, Dict

from forensic_engine.ingestion.evidence_ingestor import (
    ingest_evidence,
)


def ingest_stored_evidence(
    file_path: str | Path,
) -> Dict[str, Any]:
    """
    Run the existing forensic ingestion engine
    against a stored evidence file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Evidence file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Evidence path is not a file: {path}"
        )

    result = ingest_evidence(path)

    if not isinstance(result, dict):
        raise ValueError(
            "Forensic ingestion engine returned "
            "an invalid result."
        )

    if result.get(
        "ingestion_status"
    ) != "success":

        raise ValueError(
            "Forensic evidence ingestion failed."
        )

    required_fields = [
        "filename",
        "original_path",
        "extension",
        "mime_type",
        "size_bytes",
        "sha256",
        "imported_at",
        "ingestion_status",
    ]

    for field in required_fields:

        if field not in result:
            raise ValueError(
                f"Forensic ingestion result is "
                f"missing field: {field}"
            )

    return result


if __name__ == "__main__":

    print(
        "EVIDENCE INGESTION ADAPTER: READY"
    )
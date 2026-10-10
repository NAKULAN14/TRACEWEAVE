from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import sys

# Allow execution as:
# python forensic_engine/ingestion/evidence_ingestor.py ...
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from forensic_engine.hashing.hasher import calculate_sha256
from forensic_engine.utils.file_detector import detect_file_info


def ingest_evidence(file_path: str | Path) -> dict:
    """
    Ingest a single evidence file and return structured metadata.

    Phase 8A responsibilities:
    - filename
    - extension
    - size
    - MIME type
    - SHA-256
    - import timestamp
    """

    path = Path(file_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"Evidence file does not exist: {path}"
        )

    file_info = detect_file_info(path)

    sha256 = calculate_sha256(path)

    imported_at = datetime.now(timezone.utc).isoformat()

    evidence_record = {
        "filename": file_info["filename"],
        "original_path": str(path),
        "extension": file_info["extension"],
        "mime_type": file_info["mime_type"],
        "size_bytes": file_info["size_bytes"],
        "sha256": sha256,
        "imported_at": imported_at,
        "ingestion_status": "success"
    }

    return evidence_record


def save_ingestion_result(
    evidence_record: dict,
    output_path: str | Path
) -> None:
    """
    Save the ingestion result as JSON.
    """

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evidence_record,
            file,
            indent=4
        )


def main():
    parser = argparse.ArgumentParser(
        description="TRACEWEAVE Phase 8A - Evidence Ingestion"
    )

    parser.add_argument(
        "evidence",
        help="Path to the evidence file"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Optional path for the JSON ingestion result"
    )

    args = parser.parse_args()

    try:
        result = ingest_evidence(args.evidence)

        print("\n========================================")
        print(" TRACEWEAVE - EVIDENCE INGESTION")
        print("========================================")

        print(f"Filename     : {result['filename']}")
        print(f"Extension    : {result['extension']}")
        print(f"MIME type    : {result['mime_type']}")
        print(f"Size         : {result['size_bytes']} bytes")
        print(f"SHA-256      : {result['sha256']}")
        print(f"Imported at  : {result['imported_at']}")
        print(f"Status       : {result['ingestion_status']}")

        if args.output:
            save_ingestion_result(
                result,
                args.output
            )

            print(f"\nJSON result  : {Path(args.output).resolve()}")

        print("========================================\n")

    except Exception as error:
        print(
            f"\n[ERROR] Evidence ingestion failed: {error}",
            file=sys.stderr
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
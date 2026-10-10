"""
TRACEWEAVE - Evidence Storage Service
"""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from backend.app.config import EVIDENCE_ROOT


def generate_stored_filename(
    original_filename: str,
) -> str:
    """
    Generate a unique filename while preserving
    the original file extension.
    """

    original_path = Path(
        original_filename
    )

    extension = original_path.suffix.lower()

    unique_id = uuid4().hex

    return f"{unique_id}{extension}"


def get_case_evidence_directory(
    case_id: str,
) -> Path:
    """
    Return the evidence directory for a case.
    """

    case_directory = (
        EVIDENCE_ROOT / case_id
    )

    case_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return case_directory


async def save_uploaded_evidence(
    upload: UploadFile,
    case_id: str,
) -> tuple[str, Path, int]:

    if not upload.filename:
        raise ValueError(
            "Uploaded file must have a filename."
        )

    stored_filename = (
        generate_stored_filename(
            upload.filename
        )
    )

    case_directory = (
        get_case_evidence_directory(
            case_id
        )
    )

    destination = (
        case_directory /
        stored_filename
    )

    file_size = 0

    with destination.open("wb") as output:

        while True:

            chunk = await upload.read(
                1024 * 1024
            )

            if not chunk:
                break

            output.write(chunk)

            file_size += len(chunk)

    await upload.close()

    return (
        stored_filename,
        destination,
        file_size,
    )
if __name__ == "__main__":

    filename = generate_stored_filename(
        "suspicious_invitation.eml"
    )

    assert filename.endswith(
        ".eml"
    )

    assert filename != (
        "suspicious_invitation.eml"
    )

    print(
        "EVIDENCE STORAGE SERVICE: PASS"
    )
    print(
        "Generated filename:",
        filename,
    )
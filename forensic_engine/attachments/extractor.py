from pathlib import Path
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
import argparse
import hashlib
import json
import re
import sys


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "phase8c"


# ---------------------------------------------------------
# Hash helper
# ---------------------------------------------------------

def calculate_bytes_sha256(data: bytes) -> str:
    """
    Calculate SHA-256 hash of raw bytes.
    """
    return hashlib.sha256(data).hexdigest()


def calculate_file_sha256(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    """
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ---------------------------------------------------------
# Filename sanitization
# ---------------------------------------------------------

def sanitize_filename(filename: str | None, attachment_index: int) -> str:
    """
    Prevent path traversal and unsafe filenames.

    Example:
        ../../malicious.ics
    becomes:
        malicious.ics
    """

    if not filename:
        return f"attachment_{attachment_index}"

    # Remove any directory component
    safe_name = Path(filename).name

    # Replace unsafe characters
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", safe_name)

    # Prevent empty filenames
    if not safe_name:
        safe_name = f"attachment_{attachment_index}"

    return safe_name


# ---------------------------------------------------------
# Unique output filename
# ---------------------------------------------------------

def get_unique_output_path(
    output_directory: Path,
    filename: str,
    attachment_index: int
) -> Path:

    candidate = output_directory / filename

    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix

    return output_directory / (
        f"{stem}_{attachment_index}{suffix}"
    )


# ---------------------------------------------------------
# Extract attachments
# ---------------------------------------------------------

def extract_attachments(
    email_path: str | Path,
    output_directory: str | Path
) -> dict:

    email_path = Path(email_path).resolve()
    output_directory = Path(output_directory).resolve()

    if not email_path.is_file():
        raise FileNotFoundError(
            f"Email file not found: {email_path}"
        )

    # Create output directory
    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Parent evidence information
    # -----------------------------------------------------

    parent_hash = calculate_file_sha256(email_path)

    parent_size = email_path.stat().st_size

    # -----------------------------------------------------
    # Parse email
    # -----------------------------------------------------

    with email_path.open("rb") as file:
        message = BytesParser(
            policy=policy.default
        ).parse(file)

    extracted_attachments = []

    attachment_index = 0

    # -----------------------------------------------------
    # Walk through MIME structure
    # -----------------------------------------------------

    for part in message.walk():

        # Skip multipart containers
        if part.is_multipart():
            continue

        content_disposition = (
            part.get_content_disposition()
        )

        filename = part.get_filename()

        content_type = part.get_content_type()

        content_id = part.get("Content-ID")

        # -------------------------------------------------
        # Determine whether this is an attachment
        # -------------------------------------------------

        is_attachment = (
            content_disposition == "attachment"
            or filename is not None
        )

        if not is_attachment:
            continue

        attachment_index += 1

        # -------------------------------------------------
        # Decode attachment
        # -------------------------------------------------

        payload = part.get_payload(
            decode=True
        )

        if payload is None:
            payload = b""

        # -------------------------------------------------
        # Safe filename
        # -------------------------------------------------

        safe_filename = sanitize_filename(
            filename,
            attachment_index
        )

        # -------------------------------------------------
        # Unique destination
        # -------------------------------------------------

        destination = get_unique_output_path(
            output_directory,
            safe_filename,
            attachment_index
        )

        # -------------------------------------------------
        # Write extracted artifact
        # -------------------------------------------------

        with destination.open("wb") as output_file:
            output_file.write(payload)

        # -------------------------------------------------
        # Calculate hash
        # -------------------------------------------------

        artifact_hash = calculate_bytes_sha256(
            payload
        )

        artifact_size = len(payload)

        # -------------------------------------------------
        # Metadata
        # -------------------------------------------------

        artifact_record = {
            "attachment_index": attachment_index,

            "original_filename": filename,

            "extracted_filename": destination.name,

            "output_path": str(
                destination.relative_to(PROJECT_ROOT)
            ),

            "content_type": content_type,

            "content_disposition": (
                content_disposition
            ),

            "content_id": content_id,

            "size_bytes": artifact_size,

            "sha256": artifact_hash,

            "extraction_status": "success"
        }

        extracted_attachments.append(
            artifact_record
        )

    # -----------------------------------------------------
    # Final forensic record
    # -----------------------------------------------------

    result = {

        "parent_evidence": {

            "filename": email_path.name,

            "original_path": str(
                email_path.relative_to(PROJECT_ROOT)
            ),

            "size_bytes": parent_size,

            "sha256": parent_hash
        },

        "extraction": {

            "status": "success",

            "extracted_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "method": "MIME attachment extraction",

            "attachment_count": len(
                extracted_attachments
            )
        },

        "attachments": extracted_attachments
    }

    return result


# ---------------------------------------------------------
# Save JSON
# ---------------------------------------------------------

def save_extraction_result(
    result: dict,
    output_path: str | Path
):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False
        )


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE Phase 8C - "
            "MIME Attachment Extraction"
        )
    )

    parser.add_argument(
        "email",
        help="Path to the EML evidence file"
    )

    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Directory where extracted "
            "attachments will be stored"
        )
    )

    parser.add_argument(
        "-j",
        "--json",
        help=(
            "Path for the extraction "
            "metadata JSON"
        )
    )

    args = parser.parse_args()

    email_path = Path(args.email)

    # Default output directory
    if args.output:
        output_directory = Path(args.output)
    else:
        output_directory = (
            DEFAULT_OUTPUT_DIR
            / email_path.stem
            / "extracted"
        )

    # Default JSON path
    if args.json:
        json_path = Path(args.json)
    else:
        json_path = (
            DEFAULT_OUTPUT_DIR
            / email_path.stem
            / "attachment_extraction.json"
        )

    # -----------------------------------------------------
    # Extract
    # -----------------------------------------------------

    result = extract_attachments(
        email_path,
        output_directory
    )

    # -----------------------------------------------------
    # Save metadata
    # -----------------------------------------------------

    save_extraction_result(
        result,
        json_path
    )

    # -----------------------------------------------------
    # Console output
    # -----------------------------------------------------

    print("\nTRACEWEAVE Phase 8C")
    print("=" * 60)

    print(
        f"Parent evidence : "
        f"{result['parent_evidence']['filename']}"
    )

    print(
        f"Parent SHA-256  : "
        f"{result['parent_evidence']['sha256']}"
    )

    print(
        f"Attachments     : "
        f"{result['extraction']['attachment_count']}"
    )

    print(
        f"Output directory: "
        f"{output_directory}"
    )

    print(
        f"Metadata JSON   : "
        f"{json_path}"
    )

    print("=" * 60)

    for attachment in result["attachments"]:

        print(
            f"\n[{attachment['attachment_index']}] "
            f"{attachment['extracted_filename']}"
        )

        print(
            f"    Type : "
            f"{attachment['content_type']}"
        )

        print(
            f"    Size : "
            f"{attachment['size_bytes']} bytes"
        )

        print(
            f"    SHA256 : "
            f"{attachment['sha256']}"
        )


if __name__ == "__main__":
    main()
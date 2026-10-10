from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import hashlib
import json
import re


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PREVIEW_LENGTH = 500


# =========================================================
# SHA-256
# =========================================================

def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# =========================================================
# TEXT DECODING
# =========================================================

def decode_text(data: bytes):
    """
    Decode raw ICS bytes without modifying the original data.
    """

    try:
        return data.decode("utf-8"), "utf-8"

    except UnicodeDecodeError:
        return data.decode(
            "latin-1",
            errors="replace"
        ), "latin-1"


# =========================================================
# LINE INSPECTION
# =========================================================

def inspect_lines(text: str) -> dict:

    lines = text.splitlines()

    records = []

    for number, line in enumerate(lines, start=1):

        stripped = line.strip()

        is_begin = stripped.startswith("BEGIN:")
        is_end = stripped.startswith("END:")

        is_property = (
            ":" in stripped
            and not is_begin
            and not is_end
        )

        records.append({
            "line_number": number,
            "length": len(line),
            "text": line[:MAX_PREVIEW_LENGTH],
            "is_begin": is_begin,
            "is_end": is_end,
            "is_property": is_property
        })

    return {
        "total_lines": len(lines),
        "lines": records
    }


# =========================================================
# COMPONENT DETECTION
# =========================================================

def detect_components(lines: list[str]) -> dict:

    begin_components = []
    end_components = []

    for number, line in enumerate(lines, start=1):

        stripped = line.strip()

        begin_match = re.match(
            r"^BEGIN:([A-Za-z0-9_-]+)",
            stripped
        )

        end_match = re.match(
            r"^END:([A-Za-z0-9_-]+)",
            stripped
        )

        if begin_match:

            begin_components.append({
                "line_number": number,
                "component": begin_match.group(1)
            })

        if end_match:

            end_components.append({
                "line_number": number,
                "component": end_match.group(1)
            })

    return {
        "begin_components": begin_components,
        "end_components": end_components
    }


# =========================================================
# STRUCTURAL ANOMALIES
# =========================================================

def detect_structural_anomalies(
    lines: list[str]
) -> list[dict]:

    anomalies = []

    for number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # Empty line
        if stripped == "":

            anomalies.append({
                "line_number": number,
                "type": "EMPTY_LINE",
                "description": "Empty line detected."
            })

            continue

        # Possible malformed property
        if (
            not stripped.startswith("BEGIN:")
            and not stripped.startswith("END:")
            and ":" not in stripped
            and not stripped.startswith((" ", "\t"))
        ):

            anomalies.append({
                "line_number": number,
                "type": "MISSING_PROPERTY_DELIMITER",
                "description": (
                    "Line does not contain "
                    "a property delimiter."
                ),
                "line_preview": (
                    stripped[:MAX_PREVIEW_LENGTH]
                )
            })

    return anomalies


# =========================================================
# ENCODED DATA CANDIDATES
# =========================================================

def detect_encoded_candidates(
    text: str
) -> list[dict]:

    candidates = []

    # -----------------------------------------------------
    # Base64-like sequences
    # -----------------------------------------------------

    base64_pattern = re.compile(
        r"(?<![A-Za-z0-9+/])"
        r"(?:[A-Za-z0-9+/]{4}){4,}"
        r"(?:={0,2})"
        r"(?![A-Za-z0-9+/])"
    )

    for match in base64_pattern.finditer(text):

        candidate = match.group(0)

        try:

            decoded = base64.b64decode(
                candidate,
                validate=True
            )

            candidates.append({
                "type": "BASE64_CANDIDATE",
                "start_offset": match.start(),
                "end_offset": match.end(),
                "encoded_length": len(candidate),
                "decoded_size": len(decoded),
                "decoded_sha256": calculate_sha256(
                    decoded
                )
            })

        except Exception:
            continue

    # -----------------------------------------------------
    # Data URI
    # -----------------------------------------------------

    data_uri_pattern = re.compile(
        r"data:[^,\s]+,[^\s]+",
        re.IGNORECASE
    )

    for match in data_uri_pattern.finditer(text):

        candidates.append({
            "type": "DATA_URI_CANDIDATE",
            "start_offset": match.start(),
            "end_offset": match.end(),
            "preview": match.group(0)[
                :MAX_PREVIEW_LENGTH
            ]
        })

    return candidates


# =========================================================
# RAW ICS INSPECTION
# =========================================================

def inspect_raw_ics(
    file_path: str | Path
) -> dict:

    file_path = Path(file_path).resolve()

    if not file_path.is_file():
        raise FileNotFoundError(
            f"ICS file not found: {file_path}"
        )

    # -----------------------------------------------------
    # Read raw bytes
    # -----------------------------------------------------

    raw_data = file_path.read_bytes()

    # -----------------------------------------------------
    # Decode
    # -----------------------------------------------------

    text, encoding_used = decode_text(
        raw_data
    )

    # -----------------------------------------------------
    # Split lines
    # -----------------------------------------------------

    lines = text.splitlines()

    # -----------------------------------------------------
    # Analyse
    # -----------------------------------------------------

    line_analysis = inspect_lines(
        text
    )

    component_analysis = detect_components(
        lines
    )

    anomalies = detect_structural_anomalies(
        lines
    )

    encoded_candidates = detect_encoded_candidates(
        text
    )

    # -----------------------------------------------------
    # VCALENDAR structure
    # -----------------------------------------------------

    has_vcalendar_begin = any(
        item["component"] == "VCALENDAR"
        for item in component_analysis[
            "begin_components"
        ]
    )

    has_vcalendar_end = any(
        item["component"] == "VCALENDAR"
        for item in component_analysis[
            "end_components"
        ]
    )

    balanced_vcalendar = (
        has_vcalendar_begin
        and has_vcalendar_end
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    result = {
        "artifact": {
            "filename": file_path.name,
            "path": str(file_path),
            "size_bytes": len(raw_data),
            "sha256": calculate_sha256(raw_data)
        },

        "inspection": {
            "inspected_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "encoding_used": encoding_used
        },

        "structure": {
            "has_vcalendar_begin": (
                has_vcalendar_begin
            ),

            "has_vcalendar_end": (
                has_vcalendar_end
            ),

            "balanced_vcalendar": (
                balanced_vcalendar
            ),

            "component_analysis": (
                component_analysis
            ),

            "line_analysis": (
                line_analysis
            )
        },

        "anomalies": anomalies,

        "encoded_candidates": (
            encoded_candidates
        ),

        "raw_preview": text[:2000]
    }

    return result


# =========================================================
# SAVE JSON
# =========================================================

def save_result(
    result: dict,
    output_path: str | Path
):

    output_path = Path(
        output_path
    ).resolve()

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


# =========================================================
# COMMAND LINE
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE Phase 9C - "
            "Raw ICS Structure Inspector"
        )
    )

    parser.add_argument(
        "ics",
        help="Path to ICS artifact"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON path"
    )

    args = parser.parse_args()

    ics_path = Path(
        args.ics
    )

    result = inspect_raw_ics(
        ics_path
    )

    # -----------------------------------------------------
    # Output path
    # -----------------------------------------------------

    if args.output:

        output_path = Path(
            args.output
        )

    else:

        output_path = (
            PROJECT_ROOT
            / "reports"
            / "phase9"
            / (
                f"{ics_path.stem}"
                "_raw_inspection.json"
            )
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_result(
        result,
        output_path
    )

    # -----------------------------------------------------
    # Console output
    # -----------------------------------------------------

    print()
    print("TRACEWEAVE Phase 9C")
    print("=" * 60)

    print(
        f"Artifact             : "
        f"{result['artifact']['filename']}"
    )

    print(
        f"Size                 : "
        f"{result['artifact']['size_bytes']} bytes"
    )

    print(
        f"SHA-256              : "
        f"{result['artifact']['sha256']}"
    )

    print(
        f"Encoding             : "
        f"{result['inspection']['encoding_used']}"
    )

    print(
        f"VCALENDAR BEGIN      : "
        f"{result['structure']['has_vcalendar_begin']}"
    )

    print(
        f"VCALENDAR END        : "
        f"{result['structure']['has_vcalendar_end']}"
    )

    print(
        f"Balanced VCALENDAR   : "
        f"{result['structure']['balanced_vcalendar']}"
    )

    print(
        f"Structural anomalies : "
        f"{len(result['anomalies'])}"
    )

    print(
        f"Encoded candidates   : "
        f"{len(result['encoded_candidates'])}"
    )

    print(
        f"Output               : "
        f"{output_path}"
    )

    print("=" * 60)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
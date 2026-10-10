from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from forensic_engine.ics.ics_parser import parse_ics


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT / "reports" / "phase9" / "recovered"
)

KNOWN_PROPERTIES = {
    "VERSION",
    "PRODID",
    "CALSCALE",
    "METHOD",

    "BEGIN",
    "END",

    "UID",
    "DTSTAMP",
    "DTSTART",
    "DTEND",
    "DURATION",

    "SUMMARY",
    "DESCRIPTION",
    "LOCATION",
    "STATUS",
    "SEQUENCE",

    "ORGANIZER",
    "ATTENDEE",

    "CLASS",
    "TRANSP",

    "CREATED",
    "LAST-MODIFIED",

    "RRULE",
    "RDATE",
    "EXDATE",

    "URL",
    "COMMENT",
    "CATEGORIES",
    "CONTACT",
    "GEO",
    "PRIORITY",

    "RECURRENCE-ID",
    "ATTACH",
    "RELATED-TO",
    "RESOURCES",

    "COLOR",

    # VALARM properties
    "ACTION",
    "TRIGGER",
}


# ============================================================
# HASHING
# ============================================================

def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================
# 9D.1 — LINE / FORMAT NORMALIZATION
# ============================================================

def normalize_lines(text: str):
    """
    Normalize line endings while preserving leading
    whitespace because whitespace may represent ICS folding.
    """

    transformations = []

    raw_lines = text.splitlines()

    normalized_lines = []

    for line_number, line in enumerate(raw_lines, start=1):

        original = line

        # IMPORTANT:
        # Do NOT use strip().
        # Leading whitespace can be significant.
        normalized = line.rstrip("\r")

        if normalized != original:
            transformations.append({
                "type": "LINE_ENDING_NORMALIZATION",
                "line_number": line_number,
                "original": original,
                "recovered": normalized
            })

        normalized_lines.append(normalized)

    return normalized_lines, transformations


# ============================================================
# 9D.2 — STRUCTURAL RECONSTRUCTION
# ============================================================

def reconstruct_structure(lines):
    """
    Reconstruct missing VCALENDAR boundaries.
    """

    transformations = []

    recovered_lines = list(lines)

    # Remove only completely empty lines at the beginning
    while recovered_lines and not recovered_lines[0].strip():
        recovered_lines.pop(0)

    # Remove only completely empty lines at the end
    while recovered_lines and not recovered_lines[-1].strip():
        recovered_lines.pop()

    # --------------------------------------------------------
    # BEGIN:VCALENDAR
    # --------------------------------------------------------

    has_begin_vcalendar = any(
        line.strip().upper() == "BEGIN:VCALENDAR"
        for line in recovered_lines
    )

    if not has_begin_vcalendar:

        recovered_lines.insert(
            0,
            "BEGIN:VCALENDAR"
        )

        transformations.append({
            "type": "MISSING_COMPONENT_RECONSTRUCTION",
            "component": "VCALENDAR",
            "position": "BEGIN",
            "inserted": "BEGIN:VCALENDAR",
            "reason": "VCALENDAR begin boundary was missing"
        })

    # --------------------------------------------------------
    # END:VCALENDAR
    # --------------------------------------------------------

    has_end_vcalendar = any(
        line.strip().upper() == "END:VCALENDAR"
        for line in recovered_lines
    )

    if not has_end_vcalendar:

        recovered_lines.append(
            "END:VCALENDAR"
        )

        transformations.append({
            "type": "MISSING_COMPONENT_RECONSTRUCTION",
            "component": "VCALENDAR",
            "position": "END",
            "inserted": "END:VCALENDAR",
            "reason": "VCALENDAR end boundary was missing"
        })

    return recovered_lines, transformations


# ============================================================
# HELPER — DETECT PROPERTY
# ============================================================

def get_property_name(line: str):
    """
    Extract the property name from an ICS property line.
    """

    stripped = line.strip()

    if ":" not in stripped:
        return None

    left_side = stripped.split(":", 1)[0]

    property_name = left_side.split(";", 1)[0]

    property_name = property_name.upper()

    if property_name in KNOWN_PROPERTIES:
        return property_name

    return None


# ============================================================
# HELPER — LIKELY PROPERTY LINE
# ============================================================

def looks_like_new_property(line: str) -> bool:
    """
    Determine whether a line appears to begin a new ICS
    property/component.
    """

    stripped = line.strip()

    if not stripped:
        return False

    upper = stripped.upper()

    # Components
    if upper.startswith("BEGIN:"):
        return True

    if upper.startswith("END:"):
        return True

    # Normal properties
    property_name = get_property_name(stripped)

    if property_name:
        return True

    # Known property missing ':'
    for name in sorted(
        KNOWN_PROPERTIES,
        key=len,
        reverse=True
    ):
        if upper.startswith(name):

            remainder = stripped[len(name):]

            if not remainder:
                continue

            # Avoid matching arbitrary words like
            # "DESCRIPTIONXYZ".
            if remainder[0].isalnum():
                continue

            return True

    return False


# ============================================================
# 9D.3 — PROPERTY / FIELD RECOVERY
# ============================================================

def recover_ics_properties(lines):
    """
    Recover malformed ICS properties and broken folding.

    Important forensic behavior:

    1. Preserve valid properties.
    2. Preserve legitimate folded lines.
    3. Detect suspicious continuation lines.
    4. Recover broken continuation lines conservatively.
    5. Record every transformation.
    """

    recovered_lines = []
    transformations = []

    previous_property = None

    for line_number, line in enumerate(
        lines,
        start=1
    ):

        original_line = line
        stripped = line.strip()

        # ----------------------------------------------------
        # EMPTY LINE
        # ----------------------------------------------------

        if not stripped:

            recovered_lines.append(line)

            continue

        # ----------------------------------------------------
        # COMPONENT BOUNDARIES
        # ----------------------------------------------------

        upper = stripped.upper()

        if upper.startswith("BEGIN:"):

            recovered_lines.append(stripped)

            previous_property = None

            continue

        if upper.startswith("END:"):

            recovered_lines.append(stripped)

            previous_property = None

            continue

        # ----------------------------------------------------
        # VALID PROPERTY
        # ----------------------------------------------------

        property_name = get_property_name(stripped)

        if property_name:

            recovered_lines.append(line)

            previous_property = property_name

            continue

        # ----------------------------------------------------
        # WHITESPACE-PREFIXED LINE
        # ----------------------------------------------------
        #
        # A line beginning with whitespace can be a legitimate
        # folded line.
        #
        # We preserve it, but record it as a fold observation.
        # This is important for forensic provenance.
        # ----------------------------------------------------

        if line.startswith((" ", "\t")):

            recovered_lines.append(line)

            transformations.append({
                "type": "FOLDED_LINE_PRESERVED",
                "line_number": line_number,
                "original": original_line,
                "recovered": line,
                "property": previous_property,
                "reason": (
                    "Whitespace-prefixed continuation line "
                    "preserved as ICS folded content"
                )
            })

            continue

        # ----------------------------------------------------
        # BROKEN UNFOLDED CONTINUATION
        # ----------------------------------------------------
        #
        # Example:
        #
        # DESCRIPTION:...https://event
        # s.example.edu/tw/agenda/003
        #
        # The second line lacks ':' and does not start with
        # whitespace. If it follows a text property, treat it
        # conservatively as a broken continuation.
        # ----------------------------------------------------

        if previous_property in {
            "DESCRIPTION",
            "SUMMARY",
            "LOCATION",
            "COMMENT",
            "CONTACT",
            "URL",
            "ATTACH"
        }:

            recovered_line = " " + stripped

            recovered_lines.append(
                recovered_line
            )

            transformations.append({
                "type": "BROKEN_FOLD_RECOVERY",
                "line_number": line_number,
                "original": original_line,
                "recovered": recovered_line,
                "property": previous_property,
                "reason": (
                    "Line without property delimiter followed "
                    "a text property and was recovered as a "
                    "folded continuation"
                )
            })

            continue

        # ----------------------------------------------------
        # KNOWN PROPERTY WITHOUT ':'
        # ----------------------------------------------------

        matched_property = None

        for property_name in sorted(
            KNOWN_PROPERTIES,
            key=len,
            reverse=True
        ):

            if stripped.upper().startswith(
                property_name
            ):

                remainder = stripped[
                    len(property_name):
                ]

                if remainder and (
                    remainder[0].isalnum()
                    or remainder[0] in "-_"
                ):
                    continue

                matched_property = property_name

                break

        if matched_property:

            remainder = stripped[
                len(matched_property):
            ]

            if remainder:

                recovered_line = (
                    f"{matched_property}:{remainder}"
                )

                recovered_lines.append(
                    recovered_line
                )

                transformations.append({
                    "type": "PROPERTY_SEPARATOR_RECOVERY",
                    "line_number": line_number,
                    "original": original_line,
                    "recovered": recovered_line,
                    "property": matched_property,
                    "reason": (
                        "Known ICS property detected without "
                        "':' separator"
                    )
                })

                previous_property = matched_property

                continue

        # ----------------------------------------------------
        # UNRESOLVED
        # ----------------------------------------------------

        recovered_lines.append(line)

        transformations.append({
            "type": "UNRESOLVED_PROPERTY_STRUCTURE",
            "line_number": line_number,
            "original": original_line,
            "reason": (
                "No safe ICS property recovery rule matched"
            )
        })

        previous_property = None

    return recovered_lines, transformations


# ============================================================
# 9D.4 — REBUILD RECOVERED ICS
# ============================================================

def rebuild_ics_artifact(
    lines,
    output_path
):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    recovered_text = "\r\n".join(lines)

    if not recovered_text.endswith("\r\n"):
        recovered_text += "\r\n"

    output_path.write_text(
        recovered_text,
        encoding="utf-8",
        newline=""
    )

    return output_path


# ============================================================
# 9D.5 — VALIDATE RECOVERED ARTIFACT
# ============================================================

def validate_recovered_artifact(
    recovered_path
):

    parser_result = parse_ics(
        recovered_path
    )

    parser_status = (
        parser_result["parser"]["status"]
    )

    validation_status = (
        "SUCCESS"
        if parser_status == "SUCCESS"
        else "FAILED"
    )

    return {
        "validation_status": validation_status,

        "parser": {
            "name": parser_result["parser"]["name"],
            "status": parser_status
        },

        "error": parser_result.get("error")
    }


# ============================================================
# 9D.6 — FORENSIC PROVENANCE
# ============================================================

def build_provenance(
    original_path,
    recovered_path,
    original_hash,
    recovered_hash,
    transformations,
    validation
):

    return {

        "workflow_stage": "Phase 9D",

        "recovery_method": (
            "Conservative structural and property-level "
            "ICS reconstruction"
        ),

        "original_artifact": {
            "filename": original_path.name,
            "path": str(original_path),
            "size_bytes": original_path.stat().st_size,
            "sha256": original_hash
        },

        "recovered_artifact": {
            "filename": recovered_path.name,
            "path": str(recovered_path),
            "size_bytes": recovered_path.stat().st_size,
            "sha256": recovered_hash
        },

        "transformations": transformations,

        "transformation_count": len(
            transformations
        ),

        "validation": validation,

        "provenance": {
            "original_preserved": True,
            "recovered_written_separately": True,
            "original_modified": False,
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat()
        }
    }


# ============================================================
# COMPLETE 9D RECOVERY PIPELINE
# ============================================================

def recover_ics(
    input_path,
    output_directory=None
):

    original_path = Path(
        input_path
    ).resolve()

    if not original_path.is_file():
        raise FileNotFoundError(
            f"ICS file not found: {original_path}"
        )

    if output_directory is None:
        output_directory = DEFAULT_OUTPUT_DIR

    output_directory = Path(
        output_directory
    ).resolve()

    # --------------------------------------------------------
    # Original SHA-256
    # --------------------------------------------------------

    original_hash = calculate_sha256(
        original_path
    )

    # --------------------------------------------------------
    # Read original bytes
    # --------------------------------------------------------

    raw_data = original_path.read_bytes()

    try:

        text = raw_data.decode("utf-8")

        encoding_used = "utf-8"

    except UnicodeDecodeError:

        text = raw_data.decode(
            "latin-1"
        )

        encoding_used = "latin-1"

    transformations = []

    # ========================================================
    # 9D.1
    # ========================================================

    normalized_lines, t1 = normalize_lines(
        text
    )

    transformations.extend(t1)

    # ========================================================
    # 9D.2
    # ========================================================

    structured_lines, t2 = reconstruct_structure(
        normalized_lines
    )

    transformations.extend(t2)

    # ========================================================
    # 9D.3
    # ========================================================

    recovered_lines, t3 = recover_ics_properties(
        structured_lines
    )

    transformations.extend(t3)

    # ========================================================
    # 9D.4
    # ========================================================

    recovered_filename = (
        f"{original_path.stem}_recovered.ics"
    )

    recovered_path = (
        output_directory /
        recovered_filename
    )


    rebuild_ics_artifact(
        recovered_lines,
        recovered_path
    )

    # --------------------------------------------------------
    # Recovered SHA-256
    # --------------------------------------------------------

    recovered_hash = calculate_sha256(
        recovered_path
    )

    # ========================================================
    # 9D.5
    # ========================================================

    validation = validate_recovered_artifact(
        recovered_path
    )

    # ========================================================
    # 9D.6
    # ========================================================

    provenance = build_provenance(
        original_path=original_path,
        recovered_path=recovered_path,
        original_hash=original_hash,
        recovered_hash=recovered_hash,
        transformations=transformations,
        validation=validation
    )

    # --------------------------------------------------------
    # Recovery result
    # --------------------------------------------------------

    recovery_success = (
        validation["validation_status"]
        == "SUCCESS"
    )

    provenance["encoding"] = encoding_used

    provenance["recovery"] = {

        "status": (
            "SUCCESS"
            if recovery_success
            else "FAILED"
        ),

        "confidence": (
            "HIGH"
            if recovery_success
            else "LOW"
        )
    }

    # --------------------------------------------------------
    # Save provenance
    # --------------------------------------------------------

    json_path = (
        output_directory /
        f"{original_path.stem}_recovery.json"
    )

    json_path.write_text(
        json.dumps(
            provenance,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return provenance


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE Phase 9D "
            "Conservative ICS Recovery Engine"
        )
    )

    parser.add_argument(
        "input",
        help="Path to malformed ICS file"
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output directory"
    )

    args = parser.parse_args()

    result = recover_ics(
        input_path=args.input,
        output_directory=args.output
    )

    print()
    print("=" * 60)
    print("TRACEWEAVE - PHASE 9D ICS RECOVERY")
    print("=" * 60)

    print(
        f"Original artifact : "
        f"{result['original_artifact']['filename']}"
    )

    print(
        f"Original SHA-256  : "
        f"{result['original_artifact']['sha256']}"
    )

    print(
        f"Recovered artifact: "
        f"{result['recovered_artifact']['filename']}"
    )

    print(
        f"Recovered SHA-256 : "
        f"{result['recovered_artifact']['sha256']}"
    )

    print(
        f"Recovery status   : "
        f"{result['recovery']['status']}"
    )

    print(
        f"Confidence        : "
        f"{result['recovery']['confidence']}"
    )

    print(
        f"Validation status : "
        f"{result['validation']['validation_status']}"
    )

    print(
        f"Parser status     : "
        f"{result['validation']['parser']['status']}"
    )

    print(
        f"Transformations   : "
        f"{result['transformation_count']}"
    )

    print(
        f"Provenance JSON   : "
        f"{result['recovered_artifact']['path']}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
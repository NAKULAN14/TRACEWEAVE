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
from forensic_engine.recovery.ics_recovery import recover_ics


# ============================================================
# HASH
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
# CLASSIFY RESULT
# ============================================================

def classify_verification(
    before_status,
    after_status
):

    if (
        before_status == "SUCCESS"
        and after_status == "SUCCESS"
    ):
        return "PARSER_TOLERATED"

    if (
        before_status == "FAILED"
        and after_status == "SUCCESS"
    ):
        return "RECOVERY_SUCCESS"

    if (
        before_status == "FAILED"
        and after_status == "FAILED"
    ):
        return "RECOVERY_FAILED"

    if (
        before_status == "SUCCESS"
        and after_status == "FAILED"
    ):
        return "RECOVERY_REGRESSION"

    return "UNKNOWN"


# ============================================================
# VERIFY ONE ARTIFACT
# ============================================================

def verify_artifact(
    original_path: Path,
    output_directory: Path
):

    original_path = original_path.resolve()

    # --------------------------------------------------------
    # Original hash BEFORE recovery
    # --------------------------------------------------------

    original_hash_before = calculate_sha256(
        original_path
    )

    # --------------------------------------------------------
    # Standard parser BEFORE recovery
    # --------------------------------------------------------

    original_parser = parse_ics(
        original_path
    )

    original_parser_status = (
        original_parser["parser"]["status"]
    )

    # --------------------------------------------------------
    # Run recovery
    # --------------------------------------------------------

    recovery_result = recover_ics(
        input_path=original_path,
        output_directory=output_directory
    )

    recovered_path = Path(
        recovery_result[
            "recovered_artifact"
        ]["path"]
    )

    # --------------------------------------------------------
    # Standard parser AFTER recovery
    # --------------------------------------------------------

    recovered_parser = parse_ics(
        recovered_path
    )

    recovered_parser_status = (
        recovered_parser["parser"]["status"]
    )

    # --------------------------------------------------------
    # Original hash AFTER recovery
    # --------------------------------------------------------

    original_hash_after = calculate_sha256(
        original_path
    )

    # --------------------------------------------------------
    # Integrity
    # --------------------------------------------------------

    original_preserved = (
        original_hash_before
        == original_hash_after
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    classification = classify_verification(
        original_parser_status,
        recovered_parser_status
    )

    # --------------------------------------------------------
    # Verification status
    # --------------------------------------------------------

    if (
        classification == "PARSER_TOLERATED"
        and original_preserved
    ):
        verification_status = "SUCCESS"

    elif (
        classification == "RECOVERY_SUCCESS"
        and original_preserved
    ):
        verification_status = "SUCCESS"

    else:
        verification_status = "FAILED"

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    return {

        "verification_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "artifact": {
            "filename": original_path.name,
            "path": str(original_path)
        },

        "before_recovery": {
            "parser": original_parser[
                "parser"
            ]["name"],

            "status": original_parser_status,

            "error": original_parser.get(
                "error"
            ),

            "sha256": original_hash_before
        },

        "recovery": {
            "status": recovery_result[
                "recovery"
            ]["status"],

            "confidence": recovery_result[
                "recovery"
            ]["confidence"],

            "transformations":
                recovery_result[
                    "transformation_count"
                ]
        },

        "after_recovery": {

            "recovered_artifact":
                str(recovered_path),

            "parser": recovered_parser[
                "parser"
            ]["name"],

            "status":
                recovered_parser[
                    "parser"
                ]["status"],

            "error":
                recovered_parser.get(
                    "error"
                ),

            "sha256":
                calculate_sha256(
                    recovered_path
                )
        },

        "integrity": {

            "original_hash_before":
                original_hash_before,

            "original_hash_after":
                original_hash_after,

            "original_preserved":
                original_preserved
        },

        "classification": classification,

        "verification": {

            "verification_status":
                verification_status,

            "standard_parser_succeeded_before":
                original_parser_status
                == "SUCCESS",

            "standard_parser_succeeded_after":
                recovered_parser_status
                == "SUCCESS",

            "original_preserved":
                original_preserved
        }
    }


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE Phase 9E "
            "Recovery Verification"
        )
    )

    parser.add_argument(
        "input",
        help="Malformed ICS file"
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Verification output directory"
    )

    args = parser.parse_args()

    input_path = Path(
        args.input
    ).resolve()

    if not input_path.is_file():

        raise FileNotFoundError(
            f"File not found: {input_path}"
        )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    if args.output:

        output_directory = Path(
            args.output
        ).resolve()

    else:

        output_directory = (
            PROJECT_ROOT
            / "reports"
            / "phase9"
            / "verification"
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    result = verify_artifact(
        original_path=input_path,
        output_directory=output_directory
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    json_path = (
        output_directory
        / f"{input_path.stem}_verification.json"
    )

    json_path.write_text(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Console
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "TRACEWEAVE - PHASE 9E "
        "RECOVERY VERIFICATION"
    )
    print("=" * 60)

    print(
        f"Artifact                  : "
        f"{result['artifact']['filename']}"
    )

    print(
        f"Parser BEFORE recovery    : "
        f"{result['before_recovery']['status']}"
    )

    print(
        f"Recovery status           : "
        f"{result['recovery']['status']}"
    )

    print(
        f"Recovery confidence       : "
        f"{result['recovery']['confidence']}"
    )

    print(
        f"Transformations           : "
        f"{result['recovery']['transformations']}"
    )

    print(
        f"Parser AFTER recovery     : "
        f"{result['after_recovery']['status']}"
    )

    print(
        f"Original preserved        : "
        f"{result['integrity']['original_preserved']}"
    )

    print(
        f"Classification             : "
        f"{result['classification']}"
    )

    print(
        f"Verification status       : "
        f"{result['verification']['verification_status']}"
    )

    print(
        f"Verification JSON         : "
        f"{json_path}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
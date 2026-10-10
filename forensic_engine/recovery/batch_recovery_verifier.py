from pathlib import Path
from datetime import datetime, timezone
import csv
import json
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from forensic_engine.recovery.recovery_verifier import (
    verify_artifact
)


# ============================================================
# PATHS
# ============================================================

INPUT_DIRECTORY = (
    PROJECT_ROOT
    / "dataset"
    / "malformed_ics"
    / "corrupted"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "reports"
    / "phase9"
    / "batch_verification"
)


# ============================================================
# BATCH VERIFICATION
# ============================================================

def run_batch_verification():

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if not INPUT_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Input directory not found: "
            f"{INPUT_DIRECTORY}"
        )

    # --------------------------------------------------------
    # Find ICS files
    # --------------------------------------------------------

    ics_files = sorted(
        INPUT_DIRECTORY.glob("*.ics")
    )

    if not ics_files:
        raise FileNotFoundError(
            f"No ICS files found in: "
            f"{INPUT_DIRECTORY}"
        )

    results = []

    # --------------------------------------------------------
    # Process every case
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TRACEWEAVE - PHASE 9E.2")
    print("BATCH RECOVERY VERIFICATION")
    print("=" * 70)

    print(
        f"Input directory : {INPUT_DIRECTORY}"
    )

    print(
        f"Cases found     : {len(ics_files)}"
    )

    print("=" * 70)

    for index, ics_file in enumerate(
        ics_files,
        start=1
    ):

        print(
            f"[{index:02d}/{len(ics_files):02d}] "
            f"{ics_file.name}"
        )

        try:

            result = verify_artifact(
                original_path=ics_file,
                output_directory=(
                    OUTPUT_DIRECTORY
                    / "recovered"
                )
            )

            classification = (
                result["classification"]
            )

            verification_status = (
                result["verification"][
                    "verification_status"
                ]
            )

            before_status = (
                result["before_recovery"][
                    "status"
                ]
            )

            after_status = (
                result["after_recovery"][
                    "status"
                ]
            )

            transformations = (
                result["recovery"][
                    "transformations"
                ]
            )

            original_preserved = (
                result["integrity"][
                    "original_preserved"
                ]
            )

            print(
                f"     BEFORE : {before_status}"
            )

            print(
                f"     AFTER  : {after_status}"
            )

            print(
                f"     CLASS  : {classification}"
            )

            print(
                f"     STATUS : {verification_status}"
            )

            results.append({
                "case": ics_file.stem,
                "filename": ics_file.name,
                "parser_before": before_status,
                "parser_after": after_status,
                "classification": classification,
                "verification_status":
                    verification_status,
                "transformations":
                    transformations,
                "original_preserved":
                    original_preserved
            })

        except Exception as error:

            print(
                f"     ERROR  : {type(error).__name__}"
            )

            results.append({
                "case": ics_file.stem,
                "filename": ics_file.name,
                "parser_before": "ERROR",
                "parser_after": "ERROR",
                "classification": "ERROR",
                "verification_status": "FAILED",
                "transformations": 0,
                "original_preserved": False,
                "error": str(error)
            })

    # ========================================================
    # SUMMARY
    # ========================================================

    classifications = {}

    for result in results:

        classification = result[
            "classification"
        ]

        classifications[classification] = (
            classifications.get(
                classification,
                0
            ) + 1
        )

    verification_counts = {}

    for result in results:

        status = result[
            "verification_status"
        ]

        verification_counts[status] = (
            verification_counts.get(
                status,
                0
            ) + 1
        )

    # --------------------------------------------------------
    # Batch result
    # --------------------------------------------------------

    batch_result = {

        "workflow_stage":
            "Phase 9E.2",

        "verification_timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "input_directory":
            str(INPUT_DIRECTORY),

        "total_cases":
            len(results),

        "classification_summary":
            classifications,

        "verification_summary":
            verification_counts,

        "results":
            results
    }

    # ========================================================
    # SAVE JSON
    # ========================================================

    json_path = (
        OUTPUT_DIRECTORY
        / "phase9e_batch_verification.json"
    )

    json_path.write_text(
        json.dumps(
            batch_result,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # ========================================================
    # SAVE CSV
    # ========================================================

    csv_path = (
        OUTPUT_DIRECTORY
        / "phase9e_batch_verification.csv"
    )

    csv_fields = [
        "case",
        "filename",
        "parser_before",
        "parser_after",
        "classification",
        "verification_status",
        "transformations",
        "original_preserved"
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=csv_fields
        )

        writer.writeheader()

        for result in results:

            writer.writerow({
                field: result.get(
                    field,
                    ""
                )
                for field in csv_fields
            })

    # ========================================================
    # CONSOLE SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("PHASE 9E.2 BATCH SUMMARY")
    print("=" * 70)

    print(
        f"Total cases          : "
        f"{len(results)}"
    )

    print()

    print("Classification:")

    for classification, count in sorted(
        classifications.items()
    ):

        print(
            f"  {classification:<25} : "
            f"{count}"
        )

    print()

    print("Verification status:")

    for status, count in sorted(
        verification_counts.items()
    ):

        print(
            f"  {status:<25} : "
            f"{count}"
        )

    print()

    print(
        f"JSON report          : "
        f"{json_path}"
    )

    print(
        f"CSV report           : "
        f"{csv_path}"
    )

    print("=" * 70)

    return batch_result


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    run_batch_verification()
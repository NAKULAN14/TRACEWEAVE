from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import sys

from forensic_engine.ics.ics_parser import parse_ics


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Analyse parser status
# ---------------------------------------------------------

def analyze_parser_status(
    ics_path: str | Path
) -> dict:

    ics_path = Path(ics_path).resolve()

    if not ics_path.is_file():
        raise FileNotFoundError(
            f"ICS file not found: {ics_path}"
        )

    # -----------------------------------------------------
    # Run standard parser
    # -----------------------------------------------------

    parser_result = parse_ics(
        ics_path
    )

    parser_status = (
        parser_result["parser"]["status"]
    )

    # -----------------------------------------------------
    # Determine recovery requirement
    # -----------------------------------------------------

    if parser_status == "SUCCESS":

        recovery_required = False
        recovery_status = "NOT_REQUIRED"

    else:

        recovery_required = True
        recovery_status = "PENDING"

    # -----------------------------------------------------
    # Build forensic status record
    # -----------------------------------------------------

    result = {

        "artifact": {

            "filename": ics_path.name,

            "path": str(
                ics_path
            ),

            "size_bytes": (
                ics_path.stat().st_size
            )
        },

        "standard_parser": {

            "name": (
                parser_result[
                    "parser"
                ]["name"]
            ),

            "status": parser_status,

            "error": (
                parser_result.get(
                    "error"
                )
            )
        },

        "recovery": {

            "required": recovery_required,

            "status": recovery_status,

            "method": None,

            "recovered_artifact": None,

            "confidence": None
        },

        "analysis": {

            "analyzed_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "workflow_stage": (
                "phase_9b"
            )
        }
    }

    return result


# ---------------------------------------------------------
# Save result
# ---------------------------------------------------------

def save_status(
    result: dict,
    output_path: str | Path
):

    output_path = Path(
        output_path
    )

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
            "TRACEWEAVE Phase 9B - "
            "Parser Failure Detection"
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

    result = analyze_parser_status(
        ics_path
    )

    # -----------------------------------------------------
    # Default output
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
            / f"{ics_path.stem}_status.json"
        )

    save_status(
        result,
        output_path
    )

    # -----------------------------------------------------
    # Console
    # -----------------------------------------------------

    print()
    print("TRACEWEAVE Phase 9B")
    print("=" * 60)

    print(
        f"Artifact           : "
        f"{result['artifact']['filename']}"
    )

    print(
        f"Standard parser    : "
        f"{result['standard_parser']['name']}"
    )

    print(
        f"Parser status      : "
        f"{result['standard_parser']['status']}"
    )

    print(
        f"Recovery required  : "
        f"{result['recovery']['required']}"
    )

    print(
        f"Recovery status    : "
        f"{result['recovery']['status']}"
    )

    if result["standard_parser"]["error"]:

        print(
            f"Parser error       : "
            f"{result['standard_parser']['error']['message']}"
        )

    print(
        f"Output             : "
        f"{output_path}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
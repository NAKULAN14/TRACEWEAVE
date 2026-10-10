from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import sys

from icalendar import Calendar


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Parse ICS
# ---------------------------------------------------------

def parse_ics(file_path: str | Path) -> dict:

    file_path = Path(file_path).resolve()

    if not file_path.is_file():
        raise FileNotFoundError(
            f"ICS file not found: {file_path}"
        )

    # Read raw bytes
    raw_data = file_path.read_bytes()

    result = {
        "file": {
            "filename": file_path.name,
            "path": str(file_path),
            "size_bytes": len(raw_data)
        },

        "parser": {
            "name": "icalendar",
            "status": None,
            "parsed_at": datetime.now(
                timezone.utc
            ).isoformat()
        },

        "calendar": None,

        "error": None
    }

    # -----------------------------------------------------
    # Standard ICS parsing
    # -----------------------------------------------------

    try:

        calendar = Calendar.from_ical(
            raw_data
        )

        # -------------------------------------------------
        # Calendar properties
        # -------------------------------------------------

        calendar_properties = {}

        for key, value in calendar.items():

            try:
                calendar_properties[key] = str(value)

            except Exception:
                calendar_properties[key] = repr(value)

        # -------------------------------------------------
        # Components
        # -------------------------------------------------

        components = []

        for component in calendar.walk():

            component_type = component.name

            if component_type == "VCALENDAR":
                continue

            component_data = {
                "type": component_type,
                "properties": {}
            }

            for key, value in component.items():

                try:
                    component_data[
                        "properties"
                    ][key] = str(value)

                except Exception:
                    component_data[
                        "properties"
                    ][key] = repr(value)

            components.append(
                component_data
            )

        # -------------------------------------------------
        # Successful parse
        # -------------------------------------------------

        result["parser"]["status"] = "SUCCESS"

        result["calendar"] = {
            "properties": calendar_properties,
            "component_count": len(components),
            "components": components
        }

        return result

    except Exception as error:

        # -------------------------------------------------
        # Parser failure
        # -------------------------------------------------

        result["parser"]["status"] = "FAILED"

        result["error"] = {
            "type": type(error).__name__,
            "message": str(error)
        }

        return result


# ---------------------------------------------------------
# Save result
# ---------------------------------------------------------

def save_result(
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
            "TRACEWEAVE Phase 9A - "
            "Standard ICS Parser"
        )
    )

    parser.add_argument(
        "ics",
        help="Path to the ICS file"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON path"
    )

    args = parser.parse_args()

    ics_path = Path(args.ics)

    result = parse_ics(
        ics_path
    )

    # -----------------------------------------------------
    # Default output
    # -----------------------------------------------------

    if args.output:

        output_path = Path(args.output)

    else:

        output_path = (
            PROJECT_ROOT
            / "reports"
            / "phase9"
            / f"{ics_path.stem}_parse.json"
        )

    save_result(
        result,
        output_path
    )

    # -----------------------------------------------------
    # Console output
    # -----------------------------------------------------

    print()
    print("TRACEWEAVE Phase 9A")
    print("=" * 60)

    print(
        f"File   : {ics_path.name}"
    )

    print(
        f"Parser : {result['parser']['name']}"
    )

    print(
        f"Status : {result['parser']['status']}"
    )

    if result["parser"]["status"] == "SUCCESS":

        calendar = result["calendar"]

        print(
            f"Components : "
            f"{calendar['component_count']}"
        )

    else:

        print(
            f"Error type : "
            f"{result['error']['type']}"
        )

        print(
            f"Error      : "
            f"{result['error']['message']}"
        )

    print(
        f"Output : {output_path}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
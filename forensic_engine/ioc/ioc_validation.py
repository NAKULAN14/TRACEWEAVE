from pathlib import Path
import argparse
import json


SUPPORTED_TYPES = {
    "URL",
    "DOMAIN",
    "IPV4",
    "EMAIL",
    "MD5",
    "SHA1",
    "SHA256",
}


def validate_ioc(ioc):
    errors = []

    ioc_type = ioc.get("ioc_type")
    value = ioc.get("canonical_value")
    observation_count = ioc.get(
        "observation_count"
    )
    observations = ioc.get(
        "observations",
        []
    )

    if ioc_type not in SUPPORTED_TYPES:
        errors.append(
            f"Invalid IOC type: {ioc_type}"
        )

    if not value:
        errors.append(
            "Missing canonical IOC value"
        )

    if not isinstance(
        observation_count,
        int
    ):
        errors.append(
            "Observation count is not an integer"
        )

    elif observation_count < 1:
        errors.append(
            "IOC has no observations"
        )

    if observation_count != len(
        observations
    ):
        errors.append(
            "Observation count does not match "
            "observation list"
        )

    if not ioc.get(
        "original_values"
    ):
        errors.append(
            "Original IOC values missing"
        )

    for observation in observations:

        record = observation.get(
            "ioc",
            {}
        )

        provenance = record.get(
            "provenance",
            {}
        )

        if not record.get(
            "ioc_id"
        ):
            errors.append(
                "Observation missing IOC ID"
            )

        if not provenance.get(
            "original_preserved"
        ):
            errors.append(
                "Original value preservation missing"
            )

        evidence = observation.get(
            "observation",
            {}
        ).get(
            "evidence",
            {}
        )

        if not evidence.get(
            "artifact"
        ):
            errors.append(
                "Observation missing artifact"
            )

    return errors


def validate_dataset(data):
    errors = []

    if "summary" not in data:
        errors.append(
            "Missing summary"
        )

    if "iocs" not in data:
        errors.append(
            "Missing IOC collection"
        )
        return errors

    iocs = data["iocs"]

    identity_keys = set()

    for index, ioc in enumerate(iocs):

        ioc_errors = validate_ioc(
            ioc
        )

        for error in ioc_errors:
            errors.append(
                f"IOC {index}: {error}"
            )

        key = (
            ioc.get("ioc_type"),
            ioc.get("canonical_value")
        )

        if key in identity_keys:
            errors.append(
                f"Duplicate IOC identity: {key}"
            )

        identity_keys.add(key)

    return errors


def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE IOC Dataset Validator"
        )
    )

    parser.add_argument(
        "input_file",
        help="Deduplicated IOC JSON"
    )

    parser.add_argument(
        "--output",
        default="reports/phase12/ioc_validation.json"
    )

    args = parser.parse_args()

    input_path = Path(
        args.input_file
    )

    output_path = Path(
        args.output
    )

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    errors = validate_dataset(
        data
    )

    report = {
        "status": (
            "PASS"
            if not errors
            else "FAIL"
        ),
        "total_iocs": len(
            data.get(
                "iocs",
                []
            )
        ),
        "errors": errors,
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=2
        )

    print(
        "\n=== TRACEWEAVE IOC VALIDATION ==="
    )

    print(
        f"Total unique IOCs : "
        f"{report['total_iocs']}"
    )

    print(
        f"Errors            : "
        f"{len(errors)}"
    )

    print(
        f"Status            : "
        f"{report['status']}"
    )

    if errors:

        print("\nValidation errors:")

        for error in errors:
            print(
                f"  - {error}"
            )

    print(
        f"\nReport saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()
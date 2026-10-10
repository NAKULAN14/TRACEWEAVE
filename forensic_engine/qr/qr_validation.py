from pathlib import Path
import argparse
import json


REQUIRED_TOP_LEVEL_FIELDS = [
    "artifact",
    "extraction",
    "detection",
    "decoding",
    "classification",
    "provenance",
]


def validate_result(result):
    errors = []

    # Top-level structure
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in result:
            errors.append(f"Missing top-level field: {field}")

    artifact = result.get("artifact", {})
    extraction = result.get("extraction", {})
    detection = result.get("detection", {})
    decoding = result.get("decoding", {})
    classification = result.get("classification", {})
    provenance = result.get("provenance", {})

    # Artifact validation
    sha256 = artifact.get("sha256")

    if not sha256:
        errors.append("Missing SHA-256")

    elif len(sha256) != 64:
        errors.append("Invalid SHA-256 length")

    # Extraction validation
    if not extraction.get("extracted_at"):
        errors.append("Missing extraction timestamp")

    if "status" not in extraction:
        errors.append("Missing extraction status")

    # Detection validation
    if "qr_detected" not in detection:
        errors.append("Missing QR detection status")

    if "count" not in detection:
        errors.append("Missing QR count")

    # Decoding validation
    if "status" not in decoding:
        errors.append("Missing decoding status")

    # Classification validation
    if "type" not in classification:
        errors.append("Missing classification type")

    if "confidence" not in classification:
        errors.append("Missing classification confidence")

    # Provenance validation
    if provenance.get("original_artifact_preserved") is not True:
        errors.append(
            "Original artifact preservation not confirmed"
        )

    return errors


def validate_batch(batch_directory):
    batch_directory = Path(batch_directory)

    json_files = sorted(
        file
        for file in batch_directory.glob("*.json")
        if file.name != "batch_summary.json"
    )

    validation_results = []

    for json_file in json_files:

        try:

            with open(
                json_file,
                "r",
                encoding="utf-8"
            ) as f:
                result = json.load(f)

            errors = validate_result(result)

            validation_results.append({
                "file": json_file.name,
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
            })

        except Exception as exc:

            validation_results.append({
                "file": json_file.name,
                "status": "FAIL",
                "errors": [
                    f"Could not read JSON: {exc}"
                ],
            })

    passed = sum(
        1
        for result in validation_results
        if result["status"] == "PASS"
    )

    failed = len(validation_results) - passed

    return {
        "total_results": len(validation_results),
        "passed": passed,
        "failed": failed,
        "validation_status": (
            "PASS" if failed == 0 else "FAIL"
        ),
        "results": validation_results,
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE QR Batch Validation"
    )

    parser.add_argument(
        "batch_directory",
        help="QR batch result directory"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional validation report path"
    )

    args = parser.parse_args()

    report = validate_batch(
        args.batch_directory
    )

    print("\n=== TRACEWEAVE QR VALIDATION ===")

    print(
        f"Total results : {report['total_results']}"
    )

    print(
        f"Passed        : {report['passed']}"
    )

    print(
        f"Failed        : {report['failed']}"
    )

    print(
        f"Status        : {report['validation_status']}"
    )

    if report["failed"]:

        print("\nFailures:")

        for result in report["results"]:

            if result["status"] == "FAIL":

                print(
                    f"\n{result['file']}"
                )

                for error in result["errors"]:
                    print(f"  - {error}")

    if args.output:

        output_path = Path(args.output)

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
            f"\nValidation report saved to: "
            f"{output_path}"
        )


if __name__ == "__main__":
    main()
from pathlib import Path
import argparse
import json


REQUIRED_TOP_LEVEL_FIELDS = [
    "artifact",
    "analysis",
    "source",
    "normalization",
    "structure",
    "indicators",
    "provenance",
]


def validate_result(result):
    errors = []

    # Top-level structure
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in result:
            errors.append(
                f"Missing top-level field: {field}"
            )

    artifact = result.get("artifact", {})
    analysis = result.get("analysis", {})
    source = result.get("source", {})
    normalization = result.get(
        "normalization",
        {}
    )
    structure = result.get(
        "structure",
        {}
    )
    indicators = result.get(
        "indicators",
        {}
    )
    provenance = result.get(
        "provenance",
        {}
    )

    # Artifact
    sha256 = artifact.get("sha256")

    if not sha256:
        errors.append(
            "Missing SHA-256"
        )
    elif len(sha256) != 64:
        errors.append(
            "Invalid SHA-256 length"
        )

    # Analysis
    if not analysis.get("analyzed_at"):
        errors.append(
            "Missing analysis timestamp"
        )

    if analysis.get("status") != "SUCCESS":
        errors.append(
            "Analysis status is not SUCCESS"
        )

    # Source
    if not source.get("original_url"):
        errors.append(
            "Missing original URL"
        )

    if source.get("source_type") != "QR_PAYLOAD":
        errors.append(
            "Unexpected source type"
        )

    # Normalization
    if not normalization.get(
        "normalized_url"
    ):
        errors.append(
            "Missing normalized URL"
        )

    if "changed" not in normalization:
        errors.append(
            "Missing normalization change status"
        )

    # Structure
    required_structure = [
        "scheme",
        "hostname",
        "domain",
        "subdomain",
        "path",
        "query",
        "fragment",
    ]

    for field in required_structure:
        if field not in structure:
            errors.append(
                f"Missing URL structure field: {field}"
            )

    # Indicators
    if "count" not in indicators:
        errors.append(
            "Missing indicator count"
        )

    if "items" not in indicators:
        errors.append(
            "Missing indicator list"
        )

    # Provenance
    if provenance.get(
        "original_artifact_preserved"
    ) is not True:
        errors.append(
            "Original artifact preservation not confirmed"
        )

    if provenance.get(
        "network_access_performed"
    ) is not False:
        errors.append(
            "Network access status is not false"
        )

    return errors


def validate_batch(batch_directory):
    batch_directory = Path(
        batch_directory
    )

    json_files = sorted(
        file
        for file in batch_directory.glob(
            "*.json"
        )
        if file.name != "batch_summary.json"
    )

    results = []

    for json_file in json_files:

        try:

            with open(
                json_file,
                "r",
                encoding="utf-8"
            ) as f:
                result = json.load(f)

            errors = validate_result(
                result
            )

            results.append({
                "file": json_file.name,
                "status": (
                    "PASS"
                    if not errors
                    else "FAIL"
                ),
                "errors": errors,
            })

        except Exception as exc:

            results.append({
                "file": json_file.name,
                "status": "FAIL",
                "errors": [
                    f"Could not read JSON: {exc}"
                ],
            })

    passed = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    failed = (
        len(results) - passed
    )

    return {
        "total_results": len(results),
        "passed": passed,
        "failed": failed,
        "validation_status": (
            "PASS"
            if failed == 0
            else "FAIL"
        ),
        "results": results,
    }


def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE URL Analysis Validator"
        )
    )

    parser.add_argument(
        "batch_directory",
        help="URL batch result directory"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Validation report path"
    )

    args = parser.parse_args()

    report = validate_batch(
        args.batch_directory
    )

    print(
        "\n=== TRACEWEAVE URL VALIDATION ==="
    )

    print(
        f"Total results : "
        f"{report['total_results']}"
    )

    print(
        f"Passed        : "
        f"{report['passed']}"
    )

    print(
        f"Failed        : "
        f"{report['failed']}"
    )

    print(
        f"Status        : "
        f"{report['validation_status']}"
    )

    if report["failed"]:

        print("\nFailures:")

        for result in report["results"]:

            if result["status"] == "FAIL":

                print(
                    f"\n{result['file']}"
                )

                for error in result["errors"]:
                    print(
                        f"  - {error}"
                    )

    if args.output:

        output_path = Path(
            args.output
        )

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
from pathlib import Path
import argparse
import csv
import json

from forensic_engine.url.url_normalizer import normalize_url
from forensic_engine.url.url_parser import parse_url
from forensic_engine.url.url_indicators import analyze_url_indicators
from forensic_engine.url.url_analysis_result import (
    build_url_analysis_result
)


def analyze_qr_result(qr_result, qr_result_path):
    """
    Analyze the decoded URL contained in one Phase 10 QR result.
    """

    decoding = qr_result.get("decoding", {})

    payload = decoding.get("payload")

    if not payload:
        return None

    payload_type = (
        qr_result.get("classification", {})
        .get("type")
    )

    if payload_type != "URL":
        return None

    artifact = qr_result.get("artifact", {})

    artifact_path = artifact.get("path")

    if not artifact_path:
        raise ValueError(
            "Source artifact path missing"
        )

    normalization_result = normalize_url(
        payload
    )

    normalized_url = normalization_result[
        "normalized_url"
    ]

    parsing_result = parse_url(
        normalized_url
    )

    indicator_result = analyze_url_indicators(
        normalized_url
    )

    return build_url_analysis_result(
        artifact_path,
        payload,
        normalization_result,
        parsing_result,
        indicator_result
    )


def process_batch(
    input_directory,
    output_directory
):
    input_directory = Path(input_directory)
    output_directory = Path(output_directory)

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    qr_results = sorted(
        input_directory.glob("*.json")
    )

    results = []

    skipped = 0
    errors = 0

    for qr_result_path in qr_results:

        if qr_result_path.name == "batch_summary.json":
            continue

        print(
            f"[+] Processing: "
            f"{qr_result_path.name}"
        )

        try:

            with open(
                qr_result_path,
                "r",
                encoding="utf-8"
            ) as f:

                qr_result = json.load(f)

            result = analyze_qr_result(
                qr_result,
                qr_result_path
            )

            if result is None:

                skipped += 1

                print(
                    "    Skipped: no URL payload"
                )

                continue

            case_id = qr_result.get(
                "case_id",
                qr_result_path.stem
            )

            result["case_id"] = case_id

            output_path = (
                output_directory
                / f"{case_id}.json"
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    result,
                    f,
                    indent=2
                )

            results.append(result)

            print(
                "    Status: SUCCESS"
            )

        except Exception as exc:

            errors += 1

            print(
                f"    ERROR: {exc}"
            )

    return results, skipped, errors


def build_summary(
    results,
    skipped,
    errors
):

    total = len(results)

    indicator_counts = {}

    for result in results:

        for indicator in result.get(
            "indicators",
            {}
        ).get(
            "items",
            []
        ):

            name = indicator.get(
                "indicator",
                "UNKNOWN"
            )

            indicator_counts[name] = (
                indicator_counts.get(
                    name,
                    0
                ) + 1
            )

    return {
        "urls_analyzed": total,
        "non_url_cases_skipped": skipped,
        "processing_errors": errors,
        "indicator_counts": indicator_counts
    }


def write_csv(
    results,
    output_path
):

    rows = []

    for result in results:

        structure = result.get(
            "structure",
            {}
        )

        indicators = result.get(
            "indicators",
            {}
        )

        rows.append({
            "case_id": result.get(
                "case_id"
            ),

            "source_artifact": result.get(
                "artifact",
                {}
            ).get(
                "filename"
            ),

            "sha256": result.get(
                "artifact",
                {}
            ).get(
                "sha256"
            ),

            "original_url": result.get(
                "source",
                {}
            ).get(
                "original_url"
            ),

            "normalized_url": result.get(
                "normalization",
                {}
            ).get(
                "normalized_url"
            ),

            "scheme": structure.get(
                "scheme"
            ),

            "hostname": structure.get(
                "hostname"
            ),

            "domain": structure.get(
                "domain"
            ),

            "subdomain": structure.get(
                "subdomain"
            ),

            "port": structure.get(
                "port"
            ),

            "path": structure.get(
                "path"
            ),

            "query": structure.get(
                "query"
            ),

            "fragment": structure.get(
                "fragment"
            ),

            "indicator_count": indicators.get(
                "count",
                0
            )
        })

    fieldnames = [
        "case_id",
        "source_artifact",
        "sha256",
        "original_url",
        "normalized_url",
        "scheme",
        "hostname",
        "domain",
        "subdomain",
        "port",
        "path",
        "query",
        "fragment",
        "indicator_count"
    ]

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE Batch URL Analyzer"
        )
    )

    parser.add_argument(
        "input_directory",
        help=(
            "Phase 10 QR batch result directory"
        )
    )

    parser.add_argument(
        "--output",
        default="reports/phase11/batch_url",
        help="Output directory"
    )

    args = parser.parse_args()

    output_directory = Path(
        args.output
    )

    results, skipped, errors = process_batch(
        args.input_directory,
        output_directory
    )

    summary = build_summary(
        results,
        skipped,
        errors
    )

    summary_path = (
        output_directory
        / "batch_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=2
        )

    csv_path = (
        output_directory
        / "batch_results.csv"
    )

    write_csv(
        results,
        csv_path
    )

    print(
        "\n=== TRACEWEAVE URL BATCH SUMMARY ==="
    )

    print(
        f"URLs analyzed       : "
        f"{summary['urls_analyzed']}"
    )

    print(
        f"Non-URL cases       : "
        f"{summary['non_url_cases_skipped']}"
    )

    print(
        f"Processing errors   : "
        f"{summary['processing_errors']}"
    )

    print(
        f"Results saved to    : "
        f"{output_directory}"
    )


if __name__ == "__main__":
    main()
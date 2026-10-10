from pathlib import Path
import argparse
import csv
import json

from forensic_engine.ioc.ioc_detector import detect_iocs
from forensic_engine.ioc.ioc_normalizer import normalize_ioc
from forensic_engine.ioc.ioc_record import build_ioc_record
from forensic_engine.ioc.ioc_observation import build_observation


def process_text(
    text,
    artifact_path,
    source_location,
    extraction_method,
    parent_artifact=None,
):
    """
    Detect, normalize, and record IOCs from text.
    """

    observations = detect_iocs(text)

    records = []

    for observation in observations:

        ioc_type = observation["type"]
        original_value = observation["value"]

        try:

            normalized = normalize_ioc(
                ioc_type,
                original_value
            )

            normalized_value = normalized[
                "normalized_value"
            ]

            ioc_record = build_ioc_record(
                ioc_type=ioc_type,
                original_value=original_value,
                normalized_value=normalized_value,
                source_artifact=artifact_path,
                source_location=source_location,
            )

            ioc_id = ioc_record["ioc_id"]

            provenance = build_observation(
                ioc_id=ioc_id,
                ioc_type=ioc_type,
                value=normalized_value,
                artifact_path=artifact_path,
                extraction_method=extraction_method,
                source_location=source_location,
                parent_artifact=parent_artifact,
            )

            records.append({
                "ioc": ioc_record,
                "observation": provenance,
            })

        except Exception as exc:

            records.append({
                "error": str(exc),
                "original_type": ioc_type,
                "original_value": original_value,
            })

    return records


def process_qr_result(
    qr_result_path
):
    """
    Extract IOCs from a Phase 10 QR result.
    """

    with open(
        qr_result_path,
        "r",
        encoding="utf-8"
    ) as f:

        qr_result = json.load(f)

    artifact = qr_result.get(
        "artifact",
        {}
    )

    artifact_path = artifact.get(
        "path",
        qr_result_path.name
    )

    payload = qr_result.get(
        "decoding",
        {}
    ).get(
        "payload"
    )

    if not payload:
        return []

    return process_text(
        text=payload,
        artifact_path=artifact_path,
        source_location="decoded_payload",
        extraction_method="QR_PAYLOAD_DECODE",
    )


def process_url_result(
    url_result_path
):
    """
    Extract IOCs from a Phase 11 URL analysis result.
    """

    with open(
        url_result_path,
        "r",
        encoding="utf-8"
    ) as f:

        url_result = json.load(f)

    artifact = url_result.get(
        "artifact",
        {}
    )

    artifact_path = artifact.get(
        "path",
        url_result_path.name
    )

    original_url = url_result.get(
        "source",
        {}
    ).get(
        "original_url"
    )

    normalized_url = url_result.get(
        "normalization",
        {}
    ).get(
        "normalized_url"
    )

    text_parts = [
        value
        for value in [
            original_url,
            normalized_url,
        ]
        if value
    ]

    text = "\n".join(
        text_parts
    )

    return process_text(
        text=text,
        artifact_path=artifact_path,
        source_location="url_analysis",
        extraction_method="URL_ANALYSIS",
    )


def write_csv(
    records,
    output_path
):

    rows = []

    for record in records:

        ioc = record.get(
            "ioc",
            {}
        )

        observation = record.get(
            "observation",
            {}
        )

        evidence = observation.get(
            "evidence",
            {}
        )

        extraction = observation.get(
            "extraction",
            {}
        )

        rows.append({
            "ioc_id": ioc.get(
                "ioc_id"
            ),

            "type": ioc.get(
                "type"
            ),

            "value": ioc.get(
                "value"
            ),

            "original_value": ioc.get(
                "original_value"
            ),

            "artifact": evidence.get(
                "artifact"
            ),

            "parent_artifact": evidence.get(
                "parent_artifact"
            ),

            "source_location": evidence.get(
                "source_location"
            ),

            "extraction_method": extraction.get(
                "method"
            ),
        })

    fieldnames = [
        "ioc_id",
        "type",
        "value",
        "original_value",
        "artifact",
        "parent_artifact",
        "source_location",
        "extraction_method",
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
            "TRACEWEAVE Batch IOC Extraction"
        )
    )

    parser.add_argument(
        "--qr-input",
        default="reports/phase10/batch_qr",
        help="Phase 10 QR results"
    )

    parser.add_argument(
        "--url-input",
        default="reports/phase11/batch_url",
        help="Phase 11 URL results"
    )

    parser.add_argument(
        "--output",
        default="reports/phase12/batch_ioc",
        help="IOC output directory"
    )

    args = parser.parse_args()

    qr_directory = Path(
        args.qr_input
    )

    url_directory = Path(
        args.url_input
    )

    output_directory = Path(
        args.output
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    all_records = []

    # -------------------------
    # Process QR results
    # -------------------------

    for qr_file in sorted(
        qr_directory.glob("*.json")
    ):

        if qr_file.name == "batch_summary.json":
            continue

        print(
            f"[QR] {qr_file.name}"
        )

        try:

            records = process_qr_result(
                qr_file
            )

            all_records.extend(
                records
            )

        except Exception as exc:

            print(
                f"    ERROR: {exc}"
            )

    # -------------------------
    # Process URL results
    # -------------------------

    for url_file in sorted(
        url_directory.glob("*.json")
    ):

        if url_file.name == "batch_summary.json":
            continue

        print(
            f"[URL] {url_file.name}"
        )

        try:

            records = process_url_result(
                url_file
            )

            all_records.extend(
                records
            )

        except Exception as exc:

            print(
                f"    ERROR: {exc}"
            )

    # -------------------------
    # Save JSON
    # -------------------------

    json_path = (
        output_directory
        / "ioc_records.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_records,
            f,
            indent=2
        )

    # -------------------------
    # Save CSV
    # -------------------------

    csv_path = (
        output_directory
        / "ioc_records.csv"
    )

    write_csv(
        all_records,
        csv_path
    )

    # -------------------------
    # Summary
    # -------------------------

    type_counts = {}

    for record in all_records:

        ioc = record.get(
            "ioc",
            {}
        )

        ioc_type = ioc.get(
            "type"
        )

        if ioc_type:

            type_counts[ioc_type] = (
                type_counts.get(
                    ioc_type,
                    0
                ) + 1
            )

    summary = {
        "total_ioc_observations": len(
            all_records
        ),
        "ioc_type_counts": type_counts,
    }

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

    print(
        "\n=== TRACEWEAVE IOC BATCH SUMMARY ==="
    )

    print(
        f"Total IOC observations: "
        f"{len(all_records)}"
    )

    print(
        f"IOC types: "
        f"{type_counts}"
    )

    print(
        f"\nOutput: "
        f"{output_directory}"
    )


if __name__ == "__main__":
    main()
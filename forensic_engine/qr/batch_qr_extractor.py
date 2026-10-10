from pathlib import Path
import argparse
import csv
import json

from forensic_engine.qr.qr_detector import detect_qr
from forensic_engine.qr.qr_decoder import decode_qr
from forensic_engine.qr.qr_classifier import classify_payload
from forensic_engine.qr.qr_extraction_result import build_qr_extraction_result


def process_qr_image(image_path):
    detection_result = detect_qr(image_path)

    decoding_result = decode_qr(image_path)

    classification_result = classify_payload(
        decoding_result.get("payload")
    )

    return build_qr_extraction_result(
        image_path,
        detection_result,
        decoding_result,
        classification_result
    )


def process_dataset(input_directory, output_directory):
    input_directory = Path(input_directory)
    output_directory = Path(output_directory)

    output_directory.mkdir(parents=True, exist_ok=True)

    image_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".webp"
    }

    image_files = sorted(
        file for file in input_directory.rglob("*")
        if file.is_file() and file.suffix.lower() in image_extensions
    )

    results = []

    for image_path in image_files:

        print(f"[+] Processing: {image_path}")

        try:
            result = process_qr_image(image_path)

            case_id = image_path.parent.name

            result["case_id"] = case_id

            output_file = output_directory / f"{case_id}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            results.append(result)

            print(
                f"    Status: {result['extraction']['status']} | "
                f"Type: {result['classification']['type']}"
            )

        except Exception as exc:

            print(f"    ERROR: {exc}")

            results.append({
                "case_id": image_path.parent.name,
                "artifact": {
                    "filename": image_path.name,
                    "path": str(image_path)
                },
                "extraction": {
                    "status": "ERROR"
                },
                "error": str(exc)
            })

    return results


def build_summary(results):

    total = len(results)

    detected = sum(
        1
        for result in results
        if result.get("detection", {}).get("qr_detected") is True
    )

    decoded = sum(
        1
        for result in results
        if result.get("decoding", {}).get("status") == "SUCCESS"
    )

    errors = sum(
        1
        for result in results
        if result.get("extraction", {}).get("status") == "ERROR"
    )

    classification_counts = {}

    for result in results:

        qr_type = result.get(
            "classification",
            {}
        ).get(
            "type",
            "UNKNOWN"
        )

        classification_counts[qr_type] = (
            classification_counts.get(qr_type, 0) + 1
        )

    return {
        "total_images": total,
        "qr_detected": detected,
        "qr_decoded": decoded,
        "errors": errors,
        "detection_rate": (
            detected / total if total else 0
        ),
        "decoding_rate": (
            decoded / total if total else 0
        ),
        "classification_counts": classification_counts
    }


def write_csv(results, output_path):

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for result in results:

        rows.append({
            "case_id": result.get("case_id"),
            "filename": result.get(
                "artifact", {}
            ).get("filename"),

            "sha256": result.get(
                "artifact", {}
            ).get("sha256"),

            "qr_detected": result.get(
                "detection", {}
            ).get("qr_detected"),

            "qr_count": result.get(
                "detection", {}
            ).get("count", 0),

            "decode_status": result.get(
                "decoding", {}
            ).get("status"),

            "payload": result.get(
                "decoding", {}
            ).get("payload"),

            "decode_method": result.get(
                "decoding", {}
            ).get("method"),

            "payload_type": result.get(
                "classification", {}
            ).get("type"),

            "classification_confidence": result.get(
                "classification", {}
            ).get("confidence")
        })

    fieldnames = [
        "case_id",
        "filename",
        "sha256",
        "qr_detected",
        "qr_count",
        "decode_status",
        "payload",
        "decode_method",
        "payload_type",
        "classification_confidence"
    ]

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
        description="TRACEWEAVE Batch QR Extraction"
    )

    parser.add_argument(
        "input_directory",
        help="Directory containing QR dataset"
    )

    parser.add_argument(
        "--output",
        default="reports/phase10/batch_qr",
        help="Output directory"
    )

    args = parser.parse_args()

    output_directory = Path(args.output)

    results = process_dataset(
        args.input_directory,
        output_directory
    )

    summary = build_summary(results)

    summary_path = (
        output_directory / "batch_summary.json"
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
        output_directory / "batch_results.csv"
    )

    write_csv(
        results,
        csv_path
    )

    print("\n=== TRACEWEAVE QR BATCH SUMMARY ===")

    print(
        f"Total images : {summary['total_images']}"
    )

    print(
        f"QR detected  : {summary['qr_detected']}"
    )

    print(
        f"QR decoded   : {summary['qr_decoded']}"
    )

    print(
        f"Errors       : {summary['errors']}"
    )

    print(
        f"Detection rate: "
        f"{summary['detection_rate']:.2%}"
    )

    print(
        f"Decoding rate : "
        f"{summary['decoding_rate']:.2%}"
    )

    print(
        f"Results saved: {output_directory}"
    )


if __name__ == "__main__":
    main()
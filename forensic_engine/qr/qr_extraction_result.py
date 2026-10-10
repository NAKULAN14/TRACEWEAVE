from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def build_qr_extraction_result(
    image_path,
    detection_result,
    decoding_result,
    classification_result
):
    """
    Build a provenance-preserving QR extraction record.
    """

    image_path = Path(image_path)

    result = {
        "artifact": {
            "filename": image_path.name,
            "path": str(image_path),
            "sha256": calculate_sha256(image_path),
        },

        "extraction": {
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "status": decoding_result.get("status"),
            "qr_detected": detection_result.get("qr_detected"),
            "qr_count": detection_result.get("count", 0),
        },

        "detection": {
            "status": detection_result.get("status"),
            "qr_detected": detection_result.get("qr_detected"),
            "count": detection_result.get("count", 0),
            "detections": detection_result.get("detections", []),
        },

        "decoding": {
            "status": decoding_result.get("status"),
            "payload": decoding_result.get("payload"),
            "method": decoding_result.get("method"),
            "attempts": decoding_result.get("attempts", []),
        },

        "classification": {
            "type": classification_result.get("type"),
            "confidence": classification_result.get("confidence"),
        },

        "provenance": {
            "original_artifact_preserved": True,
            "source_artifact": image_path.name,
            "processing_engine": "TRACEWEAVE QR Extraction Engine",
        }
    }

    return result


def save_result(result, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="TRACEWEAVE QR Extraction Result Builder"
    )

    parser.add_argument(
        "image",
        help="Path to QR image"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path"
    )

    args = parser.parse_args()

    # Import the Phase 10 modules
    from forensic_engine.qr.qr_detector import detect_qr
    from forensic_engine.qr.qr_decoder import decode_qr
    from forensic_engine.qr.qr_classifier import classify_payload

    detection_result = detect_qr(args.image)

    decoding_result = decode_qr(args.image)

    classification_result = classify_payload(
        decoding_result.get("payload")
    )

    result = build_qr_extraction_result(
        args.image,
        detection_result,
        decoding_result,
        classification_result
    )

    print(json.dumps(result, indent=2))

    if args.output:
        save_result(result, args.output)
        print(f"\nSaved result to: {args.output}")


if __name__ == "__main__":
    main()
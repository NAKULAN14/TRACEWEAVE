from pathlib import Path
import argparse
import json
import re


def classify_payload(payload):
    """
    Classify a decoded QR payload into a forensic category.
    """

    if not payload:
        return {
            "type": "UNKNOWN",
            "confidence": 0.0
        }

    value = payload.strip()

    # URL
    if re.match(r"^https?://", value, re.IGNORECASE):
        return {
            "type": "URL",
            "confidence": 1.0
        }

    # Email
    if re.match(r"^mailto:", value, re.IGNORECASE):
        return {
            "type": "EMAIL",
            "confidence": 1.0
        }

    # Phone
    if re.match(r"^tel:", value, re.IGNORECASE):
        return {
            "type": "PHONE",
            "confidence": 1.0
        }

    # SMS
    if re.match(r"^sms:", value, re.IGNORECASE):
        return {
            "type": "SMS",
            "confidence": 1.0
        }

    # Wi-Fi
    if value.upper().startswith("WIFI:"):
        return {
            "type": "WIFI",
            "confidence": 1.0
        }

    # Empty payload
    if not value:
        return {
            "type": "UNKNOWN",
            "confidence": 0.0
        }

    # Default
    return {
        "type": "TEXT",
        "confidence": 0.8
    }


def classify_qr_payload(payload):
    """
    Return a complete QR payload classification result.
    """

    classification = classify_payload(payload)

    return {
        "payload": payload,
        "type": classification["type"],
        "confidence": classification["confidence"]
    }


def main():
    parser = argparse.ArgumentParser(
        description="TRACEWEAVE QR Payload Classifier"
    )

    parser.add_argument(
        "payload",
        help="Decoded QR payload"
    )

    args = parser.parse_args()

    result = classify_qr_payload(args.payload)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
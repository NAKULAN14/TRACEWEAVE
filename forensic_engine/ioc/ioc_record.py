from datetime import datetime, timezone
import argparse
import json
import uuid


SUPPORTED_TYPES = {
    "URL",
    "DOMAIN",
    "IPV4",
    "EMAIL",
    "MD5",
    "SHA1",
    "SHA256",
}


def build_ioc_record(
    ioc_type,
    original_value,
    normalized_value,
    source_artifact,
    source_location=None,
):
    """
    Build a canonical TRACEWEAVE IOC record.

    This records an observation.
    It does NOT determine maliciousness.
    """

    if ioc_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported IOC type: {ioc_type}"
        )

    if not normalized_value:
        raise ValueError(
            "Normalized IOC value cannot be empty"
        )

    return {
        "ioc_id": str(uuid.uuid4()),

        "type": ioc_type,

        "value": normalized_value,

        "original_value": original_value,

        "source": {
            "artifact": source_artifact,
            "location": source_location,
        },

        "observation": {
            "observed_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "status": "OBSERVED",

            "maliciousness": "UNDETERMINED",
        },

        "provenance": {
            "extraction_engine": (
                "TRACEWEAVE IOC Extraction Engine"
            ),

            "normalization_applied": (
                original_value != normalized_value
            ),

            "original_preserved": True,
        },
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE Canonical IOC Record Builder"
    )

    parser.add_argument(
        "ioc_type",
        choices=sorted(SUPPORTED_TYPES),
    )

    parser.add_argument(
        "original_value",
    )

    parser.add_argument(
        "normalized_value",
    )

    parser.add_argument(
        "source_artifact",
    )

    parser.add_argument(
        "--location",
        default=None,
        help="Optional source location"
    )

    args = parser.parse_args()

    try:

        result = build_ioc_record(
            args.ioc_type,
            args.original_value,
            args.normalized_value,
            args.source_artifact,
            args.location,
        )

        output = {
            "status": "SUCCESS",
            "ioc": result,
        }

    except Exception as exc:

        output = {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        json.dumps(
            output,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
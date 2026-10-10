from datetime import datetime, timezone
import argparse
import json
import uuid


def build_observation(
    ioc_id,
    ioc_type,
    value,
    artifact_path,
    extraction_method,
    source_location=None,
    parent_artifact=None,
):
    """
    Build a provenance record linking an IOC
    to its exact evidence source.
    """

    if not ioc_id:
        raise ValueError("IOC ID is required")

    if not value:
        raise ValueError("IOC value is required")

    if not artifact_path:
        raise ValueError("Artifact path is required")

    return {
        "observation_id": str(uuid.uuid4()),

        "ioc_reference": {
            "ioc_id": ioc_id,
            "type": ioc_type,
            "value": value,
        },

        "evidence": {
            "artifact": artifact_path,
            "parent_artifact": parent_artifact,
            "source_location": source_location,
        },

        "extraction": {
            "method": extraction_method,
            "observed_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },

        "provenance": {
            "direct_observation": True,
            "original_evidence_preserved": True,
        },
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE IOC Observation Builder"
    )

    parser.add_argument(
        "ioc_id"
    )

    parser.add_argument(
        "ioc_type"
    )

    parser.add_argument(
        "value"
    )

    parser.add_argument(
        "artifact"
    )

    parser.add_argument(
        "extraction_method"
    )

    parser.add_argument(
        "--location",
        default=None
    )

    parser.add_argument(
        "--parent-artifact",
        default=None
    )

    args = parser.parse_args()

    try:

        observation = build_observation(
            ioc_id=args.ioc_id,
            ioc_type=args.ioc_type,
            value=args.value,
            artifact_path=args.artifact,
            extraction_method=args.extraction_method,
            source_location=args.location,
            parent_artifact=args.parent_artifact,
        )

        result = {
            "status": "SUCCESS",
            "observation": observation,
        }

    except Exception as exc:

        result = {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        json.dumps(
            result,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
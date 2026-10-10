"""
TRACEWEAVE - Phase 17.1
Timeline Event Model
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_EVENT_TYPES = {
    "EMAIL_RECEIVED",
    "EMAIL_SENT",
    "ARTIFACT_IMPORTED",
    "ATTACHMENT_EXTRACTED",
    "ICS_PARSED",
    "QR_DETECTED",
    "QR_DECODED",
    "URL_EXTRACTED",
    "IOC_OBSERVED",
    "DNS_RESOLVED",
    "TLS_CERTIFICATE_OBSERVED",
    "INFRASTRUCTURE_CORRELATED",
}


def create_timeline_event(
    event_type: str,
    timestamp: str,
    description: str,
    source_artifact: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    event_type = event_type.upper()

    if event_type not in SUPPORTED_EVENT_TYPES:
        raise ValueError(
            f"Unsupported timeline event type: "
            f"{event_type}"
        )

    if not isinstance(
        timestamp,
        str,
    ) or not timestamp.strip():

        raise ValueError(
            "timestamp must be a non-empty string."
        )

    if not isinstance(
        description,
        str,
    ) or not description.strip():

        raise ValueError(
            "description must be a non-empty string."
        )

    if not isinstance(
        source_artifact,
        str,
    ) or not source_artifact.strip():

        raise ValueError(
            "source_artifact must be a "
            "non-empty string."
        )

    if not isinstance(
        evidence,
        dict,
    ):
        raise ValueError(
            "evidence must be a dictionary."
        )

    # Validate that the supplied timestamp is
    # actually ISO-8601 compatible.
    try:
        datetime.fromisoformat(
            timestamp.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid event timestamp: {timestamp}"
        ) from exc

    event_id = (
        f"{event_type}:"
        f"{source_artifact}:"
        f"{timestamp}"
    )

    return {
        "event_id": event_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "description": description.strip(),
        "source_artifact": source_artifact.strip(),
        "evidence": evidence,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "temporal_status": "OBSERVED",
    }


def validate_timeline_event(
    event: Dict[str, Any],
) -> None:

    required_fields = {
        "event_id",
        "event_type",
        "timestamp",
        "description",
        "source_artifact",
        "evidence",
        "created_at",
        "temporal_status",
    }

    missing = (
        required_fields
        - set(event.keys())
    )

    if missing:
        raise ValueError(
            "Timeline event missing fields: "
            f"{sorted(missing)}"
        )

    if event[
        "event_type"
    ] not in SUPPORTED_EVENT_TYPES:

        raise ValueError(
            f"Unsupported event type: "
            f"{event['event_type']}"
        )

    try:
        datetime.fromisoformat(
            event[
                "timestamp"
            ].replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as exc:
        raise ValueError(
            "Timeline event contains "
            "an invalid timestamp."
        ) from exc

    if event[
        "temporal_status"
    ] != "OBSERVED":

        raise ValueError(
            "Timeline event temporal_status "
            "must remain OBSERVED."
        )

    if not isinstance(
        event["evidence"],
        dict,
    ):
        raise ValueError(
            "Timeline event evidence "
            "must be an object."
        )
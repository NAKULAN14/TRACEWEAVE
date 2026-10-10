"""
TRACEWEAVE - Phase 17.3
Timeline Event Normalization
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.incident.timeline_event import (
    create_timeline_event,
    validate_timeline_event,
)


SOURCE_TO_EVENT_TYPE = {
    "EMAIL_HEADER": "EMAIL_RECEIVED",
    "ICS_PROPERTY": "ICS_PARSED",
    "ARTIFACT_METADATA": "ARTIFACT_IMPORTED",
    "QR_EXTRACTION": "QR_DECODED",
    "IOC_OBSERVATION": "IOC_OBSERVED",
    "DNS_EVIDENCE": "DNS_RESOLVED",
    "TLS_EVIDENCE": "TLS_CERTIFICATE_OBSERVED",
}


def normalize_timestamp(
    timestamp: str,
) -> str:

    if not isinstance(
        timestamp,
        str,
    ) or not timestamp.strip():

        raise ValueError(
            "Timestamp must be a non-empty string."
        )

    normalized = timestamp.strip().replace(
        "Z",
        "+00:00",
    )

    try:
        parsed = datetime.fromisoformat(
            normalized
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid timestamp: {timestamp}"
        ) from exc

    # If the source timestamp has no timezone,
    # do not invent one. Preserve it explicitly.
    if parsed.tzinfo is None:
        return parsed.isoformat()

    return parsed.astimezone(
        timezone.utc
    ).isoformat()


def normalize_timestamp_observation(
    observation: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        observation,
        dict,
    ):
        raise ValueError(
            "Timestamp observation must be a dictionary."
        )

    source_type = observation.get(
        "source_type"
    )

    if source_type not in SOURCE_TO_EVENT_TYPE:
        raise ValueError(
            f"Unsupported timestamp source: "
            f"{source_type}"
        )

    timestamp = normalize_timestamp(
        observation.get(
            "timestamp"
        )
    )

    source_artifact = observation.get(
        "source_artifact"
    )

    if not source_artifact:
        raise ValueError(
            "Timestamp observation has no source artifact."
        )

    source_location = observation.get(
        "source_location"
    )

    evidence = dict(
        observation.get(
            "evidence",
            {}
        )
    )

    # Preserve the original timestamp source.
    evidence[
        "timestamp_source_type"
    ] = source_type

    evidence[
        "timestamp_source_location"
    ] = source_location

    event_type = SOURCE_TO_EVENT_TYPE[
        source_type
    ]

    description = (
        f"{event_type.replace('_', ' ').title()} "
        f"observed from {source_artifact}"
    )

    event = create_timeline_event(
        event_type=event_type,
        timestamp=timestamp,
        description=description,
        source_artifact=source_artifact,
        evidence=evidence,
    )

    validate_timeline_event(
        event
    )

    return event


def normalize_timestamp_observations(
    observations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        observations,
        list,
    ):
        raise ValueError(
            "Timestamp observations must be a list."
        )

    normalized = []

    seen_ids = set()

    for observation in observations:

        event = normalize_timestamp_observation(
            observation
        )

        event_id = event[
            "event_id"
        ]

        if event_id in seen_ids:
            continue

        seen_ids.add(
            event_id
        )

        normalized.append(
            event
        )

    return normalized
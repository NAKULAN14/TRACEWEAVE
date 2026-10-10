"""
TRACEWEAVE - Phase 17.6
Timeline Provenance
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


SUPPORTED_PROVENANCE_TYPES = {
    "EMAIL_HEADER",
    "ICS_PROPERTY",
    "ARTIFACT_METADATA",
    "QR_EXTRACTION",
    "IOC_OBSERVATION",
    "DNS_EVIDENCE",
    "TLS_EVIDENCE",
}


def create_timeline_provenance(
    source_type: str,
    source_artifact: str,
    source_location: str,
    evidence_id: str = None,
    explanation: str = "",
) -> Dict[str, Any]:

    source_type = source_type.upper()

    if source_type not in (
        SUPPORTED_PROVENANCE_TYPES
    ):
        raise ValueError(
            f"Unsupported timeline provenance type: "
            f"{source_type}"
        )

    if not source_artifact:
        raise ValueError(
            "source_artifact cannot be empty."
        )

    if not source_location:
        raise ValueError(
            "source_location cannot be empty."
        )

    return {
        "source_type": source_type,
        "source_artifact": source_artifact,
        "source_location": source_location,
        "evidence_id": evidence_id,
        "explanation": explanation,
        "temporal_status": "OBSERVED",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "network_access_performed": False,
    }


def attach_timeline_provenance(
    event: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        event,
        dict,
    ):
        raise ValueError(
            "Timeline event must be a dictionary."
        )

    if not isinstance(
        provenance,
        dict,
    ):
        raise ValueError(
            "Provenance must be a dictionary."
        )

    updated_event = dict(event)

    updated_event[
        "provenance"
    ] = provenance

    return updated_event


def attach_provenance_to_timeline(
    timeline: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        timeline,
        dict,
    ):
        raise ValueError(
            "Timeline must be a dictionary."
        )

    updated_timeline = dict(
        timeline
    )

    events = []

    for event in timeline.get(
        "events",
        [],
    ):

        event_copy = dict(event)

        # If the event already contains
        # provenance, preserve it.
        if "provenance" not in event_copy:

            evidence = event_copy.get(
                "evidence",
                {}
            )

            source_type = evidence.get(
                "timestamp_source_type"
            )

            source_location = evidence.get(
                "timestamp_source_location"
            )

            if not source_type:
                raise ValueError(
                    f"Event {event.get('event_id')} "
                    "has no timestamp provenance type."
                )

            if not source_location:
                raise ValueError(
                    f"Event {event.get('event_id')} "
                    "has no timestamp provenance location."
                )

            provenance = create_timeline_provenance(
                source_type=source_type,
                source_artifact=event.get(
                    "source_artifact"
                ),
                source_location=source_location,
                evidence_id=evidence.get(
                    "evidence_id"
                ),
                explanation=(
                    "Timeline timestamp was derived "
                    "from the recorded forensic evidence."
                ),
            )

            event_copy[
                "provenance"
            ] = provenance

        events.append(
            event_copy
        )

    updated_timeline[
        "events"
    ] = events

    updated_timeline[
        "provenance_status"
    ] = "OBSERVED"

    updated_timeline[
        "provenance_created_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()

    return updated_timeline


def validate_timeline_provenance(
    provenance: Dict[str, Any],
) -> None:

    required_fields = {
        "source_type",
        "source_artifact",
        "source_location",
        "evidence_id",
        "explanation",
        "temporal_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(provenance.keys())
    )

    if missing:
        raise ValueError(
            "Timeline provenance missing fields: "
            f"{sorted(missing)}"
        )

    if provenance[
        "source_type"
    ] not in SUPPORTED_PROVENANCE_TYPES:

        raise ValueError(
            "Unsupported timeline provenance type."
        )

    if not provenance[
        "source_artifact"
    ]:

        raise ValueError(
            "Timeline provenance source artifact "
            "cannot be empty."
        )

    if not provenance[
        "source_location"
    ]:

        raise ValueError(
            "Timeline provenance source location "
            "cannot be empty."
        )

    if provenance[
        "temporal_status"
    ] != "OBSERVED":

        raise ValueError(
            "Timeline provenance must remain OBSERVED."
        )

    if provenance[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "Timeline provenance must record "
            "network_access_performed=false."
        )
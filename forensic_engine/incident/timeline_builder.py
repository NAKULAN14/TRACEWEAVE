"""
TRACEWEAVE - Phase 17.5
Incident Timeline Construction
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.incident.timeline_event import (
    validate_timeline_event,
)

from forensic_engine.incident.timeline_orderer import (
    add_sequence_numbers,
    validate_timeline_order,
)


def build_timeline(
    events: List[Dict[str, Any]],
    case_id: str,
) -> Dict[str, Any]:

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "Timeline events must be a list."
        )

    if not isinstance(
        case_id,
        str,
    ) or not case_id.strip():

        raise ValueError(
            "case_id must be a non-empty string."
        )

    # Validate every incoming event.
    for event in events:
        validate_timeline_event(
            event
        )

    # Chronologically order and number events.
    ordered_events = add_sequence_numbers(
        events
    )

    validate_timeline_order(
        ordered_events
    )

    # Calculate temporal boundaries.
    first_timestamp = None
    last_timestamp = None

    if ordered_events:

        first_timestamp = ordered_events[
            0
        ]["timestamp"]

        last_timestamp = ordered_events[
            -1
        ]["timestamp"]

    return {
        "timeline_id": (
            f"TL-{case_id.strip()}"
        ),
        "case_id": case_id.strip(),
        "timeline_type": (
            "FORENSIC_INCIDENT_TIMELINE"
        ),
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "event_count": len(
            ordered_events
        ),
        "first_event_timestamp":
            first_timestamp,
        "last_event_timestamp":
            last_timestamp,
        "temporal_status": "OBSERVED",
        "events": ordered_events,
    }


def validate_timeline(
    timeline: Dict[str, Any],
) -> None:

    required_fields = {
        "timeline_id",
        "case_id",
        "timeline_type",
        "created_at",
        "event_count",
        "first_event_timestamp",
        "last_event_timestamp",
        "temporal_status",
        "events",
    }

    missing = (
        required_fields
        - set(timeline.keys())
    )

    if missing:
        raise ValueError(
            "Timeline missing fields: "
            f"{sorted(missing)}"
        )

    if timeline[
        "timeline_type"
    ] != "FORENSIC_INCIDENT_TIMELINE":

        raise ValueError(
            "Invalid timeline type."
        )

    if timeline[
        "temporal_status"
    ] != "OBSERVED":

        raise ValueError(
            "Timeline temporal_status "
            "must remain OBSERVED."
        )

    events = timeline[
        "events"
    ]

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "Timeline events must be a list."
        )

    if timeline[
        "event_count"
    ] != len(events):

        raise ValueError(
            "Timeline event_count does not "
            "match actual event count."
        )

    # Sequence numbers must be unique.
    sequence_numbers = [
        event.get(
            "sequence_number"
        )
        for event in events
    ]

    if len(sequence_numbers) != len(
        set(sequence_numbers)
    ):
        raise ValueError(
            "Timeline contains duplicate sequence numbers."
        )

    # Validate chronological ordering.
    validate_timeline_order(
        events
    )

    if events:

        if timeline[
            "first_event_timestamp"
        ] != events[0]["timestamp"]:

            raise ValueError(
                "First-event timestamp does not "
                "match timeline."
            )

        if timeline[
            "last_event_timestamp"
        ] != events[-1]["timestamp"]:

            raise ValueError(
                "Last-event timestamp does not "
                "match timeline."
            )

    else:

        if (
            timeline[
                "first_event_timestamp"
            ] is not None
            or timeline[
                "last_event_timestamp"
            ] is not None
        ):
            raise ValueError(
                "Empty timeline must have "
                "null temporal boundaries."
            )
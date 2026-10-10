"""
TRACEWEAVE - Phase 17.4
Chronological Timeline Ordering
"""

from datetime import datetime
from typing import Any, Dict, List

from forensic_engine.incident.timeline_event import (
    validate_timeline_event,
)


def parse_event_timestamp(
    timestamp: str,
) -> datetime:

    if not isinstance(
        timestamp,
        str,
    ) or not timestamp.strip():

        raise ValueError(
            "Event timestamp must be a non-empty string."
        )

    normalized = timestamp.strip().replace(
        "Z",
        "+00:00",
    )

    try:
        return datetime.fromisoformat(
            normalized
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid event timestamp: {timestamp}"
        ) from exc


def sort_timeline_events(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "Timeline events must be a list."
        )

    validated_events = []

    for event in events:

        validate_timeline_event(
            event
        )

        # Validate timestamp before sorting.
        parse_event_timestamp(
            event["timestamp"]
        )

        validated_events.append(event)

    # Stable chronological ordering.
    #
    # event_id is used as a deterministic
    # tie-breaker when two events have the
    # exact same timestamp.
    return sorted(
        validated_events,
        key=lambda event: (
            parse_event_timestamp(
                event["timestamp"]
            ),
            event["event_id"],
        ),
    )


def add_sequence_numbers(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    ordered_events = sort_timeline_events(
        events
    )

    result = []

    for index, event in enumerate(
        ordered_events,
        start=1,
    ):

        normalized_event = dict(
            event
        )

        normalized_event[
            "sequence_number"
        ] = index

        result.append(
            normalized_event
        )

    return result


def validate_timeline_order(
    events: List[Dict[str, Any]],
) -> None:

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "Timeline events must be a list."
        )

    previous_timestamp = None
    previous_sequence = None

    for index, event in enumerate(
        events
    ):

        validate_timeline_event(
            event
        )

        timestamp = parse_event_timestamp(
            event["timestamp"]
        )

        sequence = event.get(
            "sequence_number"
        )

        if sequence is not None:

            if previous_sequence is not None:

                if sequence <= previous_sequence:
                    raise ValueError(
                        "Timeline sequence numbers "
                        "must increase."
                    )

            previous_sequence = sequence

        if previous_timestamp is not None:

            if timestamp < previous_timestamp:
                raise ValueError(
                    f"Timeline is not chronological "
                    f"at event index {index}."
                )

        previous_timestamp = timestamp
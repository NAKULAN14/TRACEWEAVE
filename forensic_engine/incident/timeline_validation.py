"""
TRACEWEAVE - Phase 17.7
Timeline Validation
"""

import json
import sys
from typing import Any, Dict, List, Set

from forensic_engine.incident.timeline_builder import (
    validate_timeline,
)

from forensic_engine.incident.timeline_provenance import (
    validate_timeline_provenance,
)


def validate_timeline_complete(
    timeline: Dict[str, Any],
) -> List[str]:

    errors: List[str] = []

    # -----------------------------------------------
    # Timeline structure
    # -----------------------------------------------

    try:
        validate_timeline(
            timeline
        )
    except Exception as exc:
        errors.append(
            f"Timeline validation failed: {exc}"
        )
        return errors

    events = timeline[
        "events"
    ]

    # -----------------------------------------------
    # Event uniqueness
    # -----------------------------------------------

    event_ids: Set[str] = set()
    sequence_numbers: Set[int] = set()

    for index, event in enumerate(events):

        event_id = event.get(
            "event_id"
        )

        if event_id in event_ids:
            errors.append(
                f"Duplicate event ID: {event_id}"
            )

        event_ids.add(
            event_id
        )

        sequence = event.get(
            "sequence_number"
        )

        if sequence in sequence_numbers:
            errors.append(
                f"Duplicate sequence number: {sequence}"
            )

        sequence_numbers.add(
            sequence
        )

        # -------------------------------------------
        # Provenance
        # -------------------------------------------

        provenance = event.get(
            "provenance"
        )

        if provenance is None:
            errors.append(
                f"Event [{index}] has no provenance."
            )
            continue

        try:
            validate_timeline_provenance(
                provenance
            )
        except Exception as exc:
            errors.append(
                f"Event [{index}] provenance invalid: {exc}"
            )

        # Provenance artifact should match
        # the event's source artifact.
        if (
            provenance.get(
                "source_artifact"
            )
            != event.get(
                "source_artifact"
            )
        ):
            errors.append(
                f"Event [{index}] provenance artifact "
                "does not match source artifact."
            )

        # -------------------------------------------
        # Evidence
        # -------------------------------------------

        if not isinstance(
            event.get("evidence"),
            dict,
        ):
            errors.append(
                f"Event [{index}] evidence must be an object."
            )

        if event.get(
            "temporal_status"
        ) != "OBSERVED":

            errors.append(
                f"Event [{index}] temporal_status "
                "must be OBSERVED."
            )

    # -----------------------------------------------
    # Sequence ordering
    # -----------------------------------------------

    expected_sequences = list(
        range(
            1,
            len(events) + 1,
        )
    )

    actual_sequences = [
        event.get(
            "sequence_number"
        )
        for event in events
    ]

    if actual_sequences != expected_sequences:
        errors.append(
            "Timeline sequence numbers are not "
            "continuous and ordered."
        )

    # -----------------------------------------------
    # Network access
    # -----------------------------------------------

    for index, event in enumerate(events):

        provenance = event.get(
            "provenance",
            {}
        )

        if provenance.get(
            "network_access_performed"
        ) is not False:

            errors.append(
                f"Event [{index}] provenance indicates "
                "network access."
            )

    return errors


def main() -> None:

    # Controlled validation fixture.
    #
    # This validates the Phase 17 structure without
    # depending on a future persisted incident file.

    timeline = {
        "timeline_id":
            "TL-TRACEWEAVE-VALIDATION",

        "case_id":
            "TRACEWEAVE-VALIDATION",

        "timeline_type":
            "FORENSIC_INCIDENT_TIMELINE",

        "created_at":
            "2026-01-01T00:00:00+00:00",

        "event_count":
            2,

        "first_event_timestamp":
            "2026-01-01T10:00:00+00:00",

        "last_event_timestamp":
            "2026-01-01T10:05:00+00:00",

        "temporal_status":
            "OBSERVED",

        "events": [
            {
                "event_id":
                    "EMAIL_RECEIVED:email.eml:"
                    "2026-01-01T10:00:00+00:00",

                "event_type":
                    "EMAIL_RECEIVED",

                "timestamp":
                    "2026-01-01T10:00:00+00:00",

                "description":
                    "Email received",

                "source_artifact":
                    "email.eml",

                "evidence": {
                    "method":
                        "EMAIL_HEADER_EXTRACTION",
                    "timestamp_source_type":
                        "EMAIL_HEADER",
                    "timestamp_source_location":
                        "Date",
                },

                "created_at":
                    "2026-01-01T10:00:00+00:00",

                "temporal_status":
                    "OBSERVED",

                "sequence_number":
                    1,

                "provenance": {
                    "source_type":
                        "EMAIL_HEADER",
                    "source_artifact":
                        "email.eml",
                    "source_location":
                        "Date",
                    "evidence_id":
                        None,
                    "explanation":
                        "Timestamp derived from "
                        "email Date header.",
                    "temporal_status":
                        "OBSERVED",
                    "created_at":
                        "2026-01-01T10:00:00+00:00",
                    "network_access_performed":
                        False,
                },
            },
            {
                "event_id":
                    "QR_DECODED:event.ics:"
                    "2026-01-01T10:05:00+00:00",

                "event_type":
                    "QR_DECODED",

                "timestamp":
                    "2026-01-01T10:05:00+00:00",

                "description":
                    "QR decoded",

                "source_artifact":
                    "event.ics",

                "evidence": {
                    "method":
                        "QR_DECODER",
                    "timestamp_source_type":
                        "QR_EXTRACTION",
                    "timestamp_source_location":
                        "embedded_qr[0]",
                },

                "created_at":
                    "2026-01-01T10:05:00+00:00",

                "temporal_status":
                    "OBSERVED",

                "sequence_number":
                    2,

                "provenance": {
                    "source_type":
                        "QR_EXTRACTION",
                    "source_artifact":
                        "event.ics",
                    "source_location":
                        "embedded_qr[0]",
                    "evidence_id":
                        None,
                    "explanation":
                        "Timestamp associated with "
                        "QR extraction evidence.",
                    "temporal_status":
                        "OBSERVED",
                    "created_at":
                        "2026-01-01T10:05:00+00:00",
                    "network_access_performed":
                        False,
                },
            },
        ],
    }

    errors = validate_timeline_complete(
        timeline
    )

    result = {
        "status":
            "PASS"
            if not errors
            else "FAIL",

        "timeline_id":
            timeline["timeline_id"],

        "event_count":
            len(timeline["events"]),

        "errors":
            errors,

        "validation_scope": [
            "timeline_schema",
            "event_uniqueness",
            "sequence_uniqueness",
            "chronological_order",
            "sequence_continuity",
            "event_provenance",
            "source_artifact_consistency",
            "temporal_status",
            "network_access_flags",
        ],
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
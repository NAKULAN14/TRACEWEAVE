"""
TRACEWEAVE - Phase 18.2
Evidence to Attack Stage Mapping
"""

from typing import Any, Dict, List

from forensic_engine.incident.attack_stage import (
    create_attack_stage,
    validate_attack_stage,
)


EVENT_TO_STAGE = {
    "EMAIL_RECEIVED": "DELIVERY",
    "EMAIL_SENT": "DELIVERY",
    "ARTIFACT_IMPORTED": "ARTIFACT_INTERACTION",
    "ATTACHMENT_EXTRACTED": "ARTIFACT_INTERACTION",
    "ICS_PARSED": "ARTIFACT_INTERACTION",
    "QR_DETECTED": "QR_DISCOVERY",
    "QR_DECODED": "QR_DECODE",
    "URL_EXTRACTED": "URL_EXTRACTION",
    "IOC_OBSERVED": "IOC_EXTRACTION",
    "DNS_RESOLVED": "INFRASTRUCTURE_CORRELATION",
    "TLS_CERTIFICATE_OBSERVED":
        "INFRASTRUCTURE_CORRELATION",
    "INFRASTRUCTURE_CORRELATED":
        "INFRASTRUCTURE_CORRELATION",
}


def map_event_to_stage(
    event: Dict[str, Any],
    sequence_number: int,
) -> Dict[str, Any]:

    if not isinstance(
        event,
        dict,
    ):
        raise ValueError(
            "Timeline event must be a dictionary."
        )

    event_type = event.get(
        "event_type"
    )

    if event_type not in EVENT_TO_STAGE:
        raise ValueError(
            f"No attack-stage mapping exists "
            f"for event type: {event_type}"
        )

    stage_type = EVENT_TO_STAGE[
        event_type
    ]

    evidence = {
        "event_id": event.get(
            "event_id"
        ),
        "event_type": event_type,
        "timestamp": event.get(
            "timestamp"
        ),
        "source_artifact": event.get(
            "source_artifact"
        ),
        "event_evidence": event.get(
            "evidence",
            {},
        ),
        "mapping_method":
            "TIMELINE_EVENT_TO_STAGE",
        "confidence": "OBSERVED",
    }

    stage = create_attack_stage(
        stage_type=stage_type,
        sequence_number=sequence_number,
        description=(
            f"{stage_type.replace('_', ' ').title()} "
            f"supported by observed "
            f"{event_type.replace('_', ' ').lower()}."
        ),
        evidence=evidence,
    )

    validate_attack_stage(
        stage
    )

    return stage


def map_timeline_to_stages(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "Timeline events must be a list."
        )

    stages = []

    seen_stage_types = set()

    for event in events:

        event_type = event.get(
            "event_type"
        )

        if event_type not in EVENT_TO_STAGE:
            continue

        stage_type = EVENT_TO_STAGE[
            event_type
        ]

        # Multiple events may support the
        # same stage. Keep one stage while
        # preserving all supporting events.
        if stage_type in seen_stage_types:

            existing = next(
                stage
                for stage in stages
                if stage["stage_type"]
                == stage_type
            )

            existing[
                "evidence"
            ].setdefault(
                "supporting_events",
                [],
            ).append(
                {
                    "event_id":
                        event.get(
                            "event_id"
                        ),
                    "event_type":
                        event_type,
                    "timestamp":
                        event.get(
                            "timestamp"
                        ),
                    "source_artifact":
                        event.get(
                            "source_artifact"
                        ),
                }
            )

            continue

        stage = map_event_to_stage(
            event,
            len(stages) + 1,
        )

        stage[
            "evidence"
        ]["supporting_events"] = [
            {
                "event_id":
                    event.get(
                        "event_id"
                    ),
                "event_type":
                    event_type,
                "timestamp":
                    event.get(
                        "timestamp"
                    ),
                "source_artifact":
                    event.get(
                        "source_artifact"
                    ),
            }
        ]

        stages.append(
            stage
        )

        seen_stage_types.add(
            stage_type
        )

    return stages
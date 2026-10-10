"""
TRACEWEAVE - Phase 20.2
Evidence to Risk Factor Mapping
"""

from typing import Any, Dict


EVENT_RISK_MAPPING = {
    "EMAIL_RECEIVED": {
        "category": "DELIVERY",
        "severity": "MEDIUM",
        "description":
            "An email delivery event was observed.",
    },
    "ATTACHMENT_EXTRACTED": {
        "category": "DELIVERY",
        "severity": "MEDIUM",
        "description":
            "An attachment was extracted from an email artifact.",
    },
    "QR_DETECTED": {
        "category": "QR_EXPOSURE",
        "severity": "MEDIUM",
        "description":
            "A QR code was detected in an investigated artifact.",
    },
    "QR_DECODED": {
        "category": "QR_EXPOSURE",
        "severity": "HIGH",
        "description":
            "A QR code was successfully decoded.",
    },
    "URL_EXTRACTED": {
        "category": "URL_EXPOSURE",
        "severity": "HIGH",
        "description":
            "A URL was extracted from an investigated artifact.",
    },
    "IOC_OBSERVED": {
        "category": "IOC_EXPOSURE",
        "severity": "HIGH",
        "description":
            "An observable indicator of compromise was extracted.",
    },
    "DNS_RESOLVED": {
        "category": "INFRASTRUCTURE",
        "severity": "MEDIUM",
        "description":
            "DNS resolution evidence was observed for an identified domain.",
    },
    "TLS_CERTIFICATE_OBSERVED": {
        "category": "INFRASTRUCTURE",
        "severity": "MEDIUM",
        "description":
            "TLS certificate evidence was observed for identified infrastructure.",
    },
}


def map_event_to_risk_factor(
    event: Dict[str, Any],
    factor_number: int,
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

    if event_type not in EVENT_RISK_MAPPING:
        raise ValueError(
            f"No risk mapping exists for "
            f"event type: {event_type}"
        )

    mapping = EVENT_RISK_MAPPING[
        event_type
    ]

    return {
        "factor_id":
            f"RF-{factor_number:03d}",
        "category":
            mapping["category"],
        "severity":
            mapping["severity"],
        "description":
            mapping["description"],
        "evidence": {
            "source_event":
                event.get("event_id"),
            "event_type":
                event_type,
            "timestamp":
                event.get("timestamp"),
            "source_artifact":
                event.get("source_artifact"),
            "event_evidence":
                event.get("evidence", {}),
            "mapping_method":
                "TIMELINE_EVENT_TO_RISK_FACTOR",
        },
        "assessment_status":
            "OBSERVED",
    }


def map_events_to_risk_factors(
    events: list,
) -> list:

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "events must be a list."
        )

    factors = []

    for event in events:

        event_type = event.get(
            "event_type"
        )

        if event_type not in EVENT_RISK_MAPPING:
            continue

        factor = map_event_to_risk_factor(
            event,
            len(factors) + 1,
        )

        factors.append(
            factor
        )

    return factors


def validate_risk_mapping(
    factor: Dict[str, Any],
) -> None:

    required_fields = {
        "factor_id",
        "category",
        "severity",
        "description",
        "evidence",
        "assessment_status",
    }

    missing = (
        required_fields
        - set(factor.keys())
    )

    if missing:
        raise ValueError(
            "Risk mapping missing fields: "
            f"{sorted(missing)}"
        )

    evidence = factor[
        "evidence"
    ]

    if not evidence.get(
        "source_event"
    ):
        raise ValueError(
            "Risk factor must reference "
            "a source event."
        )

    if not evidence.get(
        "source_artifact"
    ):
        raise ValueError(
            "Risk factor must reference "
            "a source artifact."
        )

    if factor[
        "assessment_status"
    ] != "OBSERVED":

        raise ValueError(
            "Risk assessment status must "
            "remain OBSERVED."
        )


if __name__ == "__main__":

    test_events = [
        {
            "event_id": "EVENT-001",
            "event_type": "EMAIL_RECEIVED",
            "timestamp":
                "2026-10-08T10:00:00Z",
            "source_artifact":
                "email.eml",
            "evidence": {
                "method": "EMAIL_HEADER"
            },
        },
        {
            "event_id": "EVENT-002",
            "event_type": "QR_DECODED",
            "timestamp":
                "2026-10-08T10:02:00Z",
            "source_artifact":
                "event.ics",
            "evidence": {
                "method": "QR_DECODER"
            },
        },
        {
            "event_id": "EVENT-003",
            "event_type": "URL_EXTRACTED",
            "timestamp":
                "2026-10-08T10:03:00Z",
            "source_artifact":
                "event.ics",
            "evidence": {
                "method": "URL_EXTRACTION"
            },
        },
    ]

    factors = map_events_to_risk_factors(
        test_events
    )

    for factor in factors:
        validate_risk_mapping(
            factor
        )

    print(
        "EVIDENCE → RISK MAPPING: PASS"
    )

    for factor in factors:
        print(
            factor["factor_id"],
            factor["category"],
            factor["severity"],
        )
"""
TRACEWEAVE - Phase 21.5
Recommendation Provenance
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


SUPPORTED_DERIVATION_TYPES = {
    "RISK_TO_RECOMMENDATION",
    "RECOMMENDATION_PRIORITIZATION",
    "EVIDENCE_TO_RECOMMENDATION",
}


def create_recommendation_provenance(
    recommendation_id: str,
    source_factor_id: str,
    source_event: str,
    source_artifact: str,
    derivation_type: str,
    explanation: str,
) -> Dict[str, Any]:

    if derivation_type not in SUPPORTED_DERIVATION_TYPES:
        raise ValueError(
            f"Unsupported derivation type: "
            f"{derivation_type}"
        )

    if not recommendation_id:
        raise ValueError(
            "recommendation_id is required."
        )

    if not source_factor_id:
        raise ValueError(
            "source_factor_id is required."
        )

    if not source_event:
        raise ValueError(
            "source_event is required."
        )

    if not source_artifact:
        raise ValueError(
            "source_artifact is required."
        )

    if not explanation:
        raise ValueError(
            "explanation is required."
        )

    return {
        "recommendation_id": recommendation_id,
        "source_factor_id": source_factor_id,
        "source_event": source_event,
        "source_artifact": source_artifact,
        "derivation_type": derivation_type,
        "explanation": explanation,
        "recommendation_status": "OBSERVED",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "network_access_performed": False,
    }


def attach_recommendation_provenance(
    recommendation: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(recommendation, dict):
        raise ValueError(
            "recommendation must be a dictionary."
        )

    validate_recommendation_provenance(
        provenance
    )

    if (
        provenance["recommendation_id"]
        != recommendation["recommendation_id"]
    ):
        raise ValueError(
            "Provenance recommendation ID does "
            "not match recommendation."
        )

    recommendation[
        "provenance"
    ] = provenance

    return recommendation


def validate_recommendation_provenance(
    provenance: Dict[str, Any],
) -> None:

    if not isinstance(provenance, dict):
        raise ValueError(
            "provenance must be a dictionary."
        )

    required_fields = [
        "recommendation_id",
        "source_factor_id",
        "source_event",
        "source_artifact",
        "derivation_type",
        "explanation",
        "recommendation_status",
        "created_at",
        "network_access_performed",
    ]

    for field in required_fields:
        if field not in provenance:
            raise ValueError(
                f"Missing provenance field: {field}"
            )

    if (
        provenance["derivation_type"]
        not in SUPPORTED_DERIVATION_TYPES
    ):
        raise ValueError(
            "Invalid recommendation derivation type."
        )

    if (
        provenance["recommendation_status"]
        != "OBSERVED"
    ):
        raise ValueError(
            "Recommendation provenance must "
            "remain OBSERVED."
        )

    if (
        provenance["network_access_performed"]
        is not False
    ):
        raise ValueError(
            "Recommendation provenance must "
            "record network_access_performed=False."
        )

    try:
        datetime.fromisoformat(
            provenance["created_at"]
        )
    except ValueError as exc:
        raise ValueError(
            "Invalid provenance timestamp."
        ) from exc


if __name__ == "__main__":

    recommendation = {
        "recommendation_id": "REC-001",
        "action_type": "PRESERVE_EVIDENCE",
        "title": "Preserve evidence",
        "description":
            "Preserve the original artifact.",
        "priority": "HIGH",
        "evidence": {
            "source_factor_id": "RF-001",
            "source_event": "EVENT-001",
            "source_artifact": "event.ics",
        },
        "recommendation_status": "OBSERVED",
    }

    provenance = (
        create_recommendation_provenance(
            recommendation_id="REC-001",
            source_factor_id="RF-001",
            source_event="EVENT-001",
            source_artifact="event.ics",
            derivation_type=
                "RISK_TO_RECOMMENDATION",
            explanation=(
                "Recommendation generated from "
                "the observed risk factor RF-001."
            ),
        )
    )

    attach_recommendation_provenance(
        recommendation,
        provenance,
    )

    validate_recommendation_provenance(
        recommendation["provenance"]
    )

    print(
        "RECOMMENDATION PROVENANCE: PASS"
    )
    print(
        recommendation["provenance"]
    )
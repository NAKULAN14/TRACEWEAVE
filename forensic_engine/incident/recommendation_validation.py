"""
TRACEWEAVE - Phase 21.6
Recommendation Validation
"""

from typing import Any, Dict, List

from forensic_engine.incident.recommendation import (
    validate_recommendation,
)

from forensic_engine.incident.recommendation_provenance import (
    validate_recommendation_provenance,
)

from forensic_engine.incident.recommendation_prioritizer import (
    PRIORITY_ORDER,
)


def validate_recommendation_set(
    recommendations: List[Dict[str, Any]],
) -> None:

    if not isinstance(recommendations, list):
        raise ValueError(
            "Recommendations must be a list."
        )

    recommendation_ids = set()

    expected_sequence = 1
    previous_priority = 0

    for recommendation in recommendations:

        # -------------------------------------------------
        # 1. Base recommendation validation
        # -------------------------------------------------

        validate_recommendation(
            recommendation
        )

        recommendation_id = (
            recommendation["recommendation_id"]
        )

        if recommendation_id in recommendation_ids:
            raise ValueError(
                f"Duplicate recommendation ID: "
                f"{recommendation_id}"
            )

        recommendation_ids.add(
            recommendation_id
        )

        # -------------------------------------------------
        # 2. Evidence validation
        # -------------------------------------------------

        evidence = recommendation.get(
            "evidence"
        )

        if not isinstance(evidence, dict):
            raise ValueError(
                f"Missing evidence for "
                f"{recommendation_id}"
            )

        required_evidence = [
            "source_factor_id",
            "source_event",
            "source_artifact",
        ]

        for field in required_evidence:
            if not evidence.get(field):
                raise ValueError(
                    f"Missing evidence field "
                    f"{field} for "
                    f"{recommendation_id}"
                )

        # -------------------------------------------------
        # 3. Priority validation
        # -------------------------------------------------

        priority = recommendation["priority"]

        current_priority = PRIORITY_ORDER[
            priority
        ]

        if current_priority < previous_priority:
            raise ValueError(
                "Recommendations are not ordered "
                "by priority."
            )

        priority_sequence = recommendation.get(
            "priority_sequence"
        )

        if priority_sequence != expected_sequence:
            raise ValueError(
                f"Invalid priority sequence for "
                f"{recommendation_id}"
            )

        previous_priority = current_priority
        expected_sequence += 1

        # -------------------------------------------------
        # 4. Provenance validation
        # -------------------------------------------------

        provenance = recommendation.get(
            "provenance"
        )

        if not isinstance(provenance, dict):
            raise ValueError(
                f"Missing provenance for "
                f"{recommendation_id}"
            )

        validate_recommendation_provenance(
            provenance
        )

        # -------------------------------------------------
        # 5. Recommendation ↔ provenance consistency
        # -------------------------------------------------

        if (
            provenance["recommendation_id"]
            != recommendation_id
        ):
            raise ValueError(
                "Recommendation ID does not match "
                "provenance."
            )

        if (
            provenance["source_factor_id"]
            != evidence["source_factor_id"]
        ):
            raise ValueError(
                "Source factor mismatch between "
                "evidence and provenance."
            )

        if (
            provenance["source_event"]
            != evidence["source_event"]
        ):
            raise ValueError(
                "Source event mismatch between "
                "evidence and provenance."
            )

        if (
            provenance["source_artifact"]
            != evidence["source_artifact"]
        ):
            raise ValueError(
                "Source artifact mismatch between "
                "evidence and provenance."
            )

        # -------------------------------------------------
        # 6. Network access safety
        # -------------------------------------------------

        if (
            recommendation.get(
                "network_access_performed",
                False,
            )
            is not False
        ):
            raise ValueError(
                f"Recommendation "
                f"{recommendation_id} cannot "
                f"claim network access."
            )


def build_validated_recommendation_set(
    recommendations: List[Dict[str, Any]],
) -> Dict[str, Any]:

    validate_recommendation_set(
        recommendations
    )

    priorities = {}

    for recommendation in recommendations:

        priority = recommendation[
            "priority"
        ]

        priorities[priority] = (
            priorities.get(priority, 0) + 1
        )

    return {
        "recommendation_type":
            "TRACEWEAVE_RESPONSE_RECOMMENDATIONS",
        "schema_version": "1.0",
        "status": "OBSERVED",
        "recommendation_count":
            len(recommendations),
        "priority_counts": priorities,
        "recommendations": recommendations,
        "network_access_performed": False,
    }


if __name__ == "__main__":

    recommendations = [

        {
            "recommendation_id": "REC-003",
            "action_type": "ISOLATE_ENDPOINT",
            "title": "Isolate endpoint",
            "description":
                "Isolate the affected endpoint "
                "for further investigation.",
            "priority": "CRITICAL",
            "priority_sequence": 1,
            "evidence": {
                "source_factor_id": "RF-003",
                "source_event": "EVENT-003",
                "source_artifact": "endpoint.log",
            },
            "recommendation_status": "OBSERVED",
            "network_access_performed": False,
            "provenance": {
                "recommendation_id": "REC-003",
                "source_factor_id": "RF-003",
                "source_event": "EVENT-003",
                "source_artifact": "endpoint.log",
                "derivation_type":
                    "RISK_TO_RECOMMENDATION",
                "explanation":
                    "Generated from the observed "
                    "critical execution risk factor.",
                "recommendation_status": "OBSERVED",
                "created_at":
                    "2026-10-08T10:00:00+00:00",
                "network_access_performed": False,
            },
        },

        {
            "recommendation_id": "REC-002",
            "action_type": "BLOCK_IOC",
            "title": "Review IOC blocking",
            "description":
                "Review the observed IOC for "
                "blocking.",
            "priority": "HIGH",
            "priority_sequence": 2,
            "evidence": {
                "source_factor_id": "RF-002",
                "source_event": "EVENT-002",
                "source_artifact": "qr.png",
            },
            "recommendation_status": "OBSERVED",
            "network_access_performed": False,
            "provenance": {
                "recommendation_id": "REC-002",
                "source_factor_id": "RF-002",
                "source_event": "EVENT-002",
                "source_artifact": "qr.png",
                "derivation_type":
                    "RISK_TO_RECOMMENDATION",
                "explanation":
                    "Generated from the observed "
                    "URL exposure risk factor.",
                "recommendation_status": "OBSERVED",
                "created_at":
                    "2026-10-08T10:00:00+00:00",
                "network_access_performed": False,
            },
        },

        {
            "recommendation_id": "REC-001",
            "action_type": "PRESERVE_EVIDENCE",
            "title": "Preserve evidence",
            "description":
                "Preserve the original artifact "
                "for forensic analysis.",
            "priority": "MEDIUM",
            "priority_sequence": 3,
            "evidence": {
                "source_factor_id": "RF-001",
                "source_event": "EVENT-001",
                "source_artifact": "event.ics",
            },
            "recommendation_status": "OBSERVED",
            "network_access_performed": False,
            "provenance": {
                "recommendation_id": "REC-001",
                "source_factor_id": "RF-001",
                "source_event": "EVENT-001",
                "source_artifact": "event.ics",
                "derivation_type":
                    "RISK_TO_RECOMMENDATION",
                "explanation":
                    "Generated from the observed "
                    "delivery risk factor.",
                "recommendation_status": "OBSERVED",
                "created_at":
                    "2026-10-08T10:00:00+00:00",
                "network_access_performed": False,
            },
        },
    ]

    validated = (
        build_validated_recommendation_set(
            recommendations
        )
    )

    print(
        "RECOMMENDATION VALIDATION: PASS"
    )

    print(
        "Recommendation count:",
        validated[
            "recommendation_count"
        ],
    )

    print(
        "Priority counts:",
        validated[
            "priority_counts"
        ],
    )
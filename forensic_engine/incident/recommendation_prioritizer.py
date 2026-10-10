"""
TRACEWEAVE - Phase 21.4
Recommendation Prioritization
"""

from typing import Any, Dict, List

from forensic_engine.incident.recommendation import (
    validate_recommendation,
)


PRIORITY_ORDER = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
}


def prioritize_recommendations(
    recommendations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        recommendations,
        list,
    ):
        raise ValueError(
            "recommendations must be a list."
        )

    for recommendation in recommendations:
        validate_recommendation(
            recommendation
        )

    # Stable sorting preserves the original
    # order when priorities are equal.
    prioritized = sorted(
        recommendations,
        key=lambda recommendation: (
            PRIORITY_ORDER[
                recommendation["priority"]
            ]
        ),
    )

    # Assign an explicit execution/display
    # priority sequence.
    for index, recommendation in enumerate(
        prioritized,
        start=1,
    ):
        recommendation[
            "priority_sequence"
        ] = index

    return prioritized


def validate_recommendation_prioritization(
    recommendations: List[Dict[str, Any]],
) -> None:

    if not isinstance(
        recommendations,
        list,
    ):
        raise ValueError(
            "recommendations must be a list."
        )

    expected_sequence = 1
    previous_priority = 0

    recommendation_ids = set()

    for recommendation in recommendations:

        validate_recommendation(
            recommendation
        )

        recommendation_id = (
            recommendation[
                "recommendation_id"
            ]
        )

        if recommendation_id in (
            recommendation_ids
        ):
            raise ValueError(
                f"Duplicate recommendation ID: "
                f"{recommendation_id}"
            )

        recommendation_ids.add(
            recommendation_id
        )

        priority = recommendation[
            "priority"
        ]

        current_priority = PRIORITY_ORDER[
            priority
        ]

        if current_priority < previous_priority:
            raise ValueError(
                "Recommendations are not ordered "
                "by priority."
            )

        if recommendation.get(
            "priority_sequence"
        ) != expected_sequence:

            raise ValueError(
                "Recommendation priority sequence "
                "is not continuous."
            )

        previous_priority = current_priority
        expected_sequence += 1


if __name__ == "__main__":

    test_recommendations = [
        {
            "recommendation_id": "REC-001",
            "action_type": "PRESERVE_EVIDENCE",
            "title": "Preserve evidence",
            "description":
                "Preserve the original artifact.",
            "priority": "MEDIUM",
            "evidence": {
                "source_factor_id": "RF-001",
                "source_event": "EVENT-001",
                "source_artifact": "event.ics",
            },
            "recommendation_status": "OBSERVED",
        },
        {
            "recommendation_id": "REC-002",
            "action_type": "BLOCK_IOC",
            "title": "Review IOC blocking",
            "description":
                "Review the IOC for blocking.",
            "priority": "HIGH",
            "evidence": {
                "source_factor_id": "RF-002",
                "source_event": "EVENT-002",
                "source_artifact": "qr.png",
            },
            "recommendation_status": "OBSERVED",
        },
        {
            "recommendation_id": "REC-003",
            "action_type": "DOCUMENT_FINDING",
            "title": "Document finding",
            "description":
                "Document the observed finding.",
            "priority": "CRITICAL",
            "evidence": {
                "source_factor_id": "RF-003",
                "source_event": "EVENT-003",
                "source_artifact": "email.eml",
            },
            "recommendation_status": "OBSERVED",
        },
    ]

    prioritized = prioritize_recommendations(
        test_recommendations
    )

    validate_recommendation_prioritization(
        prioritized
    )

    print(
        "RECOMMENDATION PRIORITIZATION: PASS"
    )

    for recommendation in prioritized:
        print(
            recommendation[
                "priority_sequence"
            ],
            recommendation[
                "recommendation_id"
            ],
            recommendation[
                "priority"
            ],
        )
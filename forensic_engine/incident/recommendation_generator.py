"""
TRACEWEAVE - Phase 21.3
Evidence-Based Recommendation Generation
"""

from typing import Any, Dict, List

from forensic_engine.incident.recommendation import (
    create_recommendation,
    validate_recommendation,
)


def generate_recommendations(
    mapped_recommendations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        mapped_recommendations,
        list,
    ):
        raise ValueError(
            "mapped_recommendations must be a list."
        )

    recommendations = []

    for mapped in mapped_recommendations:

        evidence = mapped.get(
            "evidence",
            {},
        )

        recommendation = create_recommendation(
            recommendation_id=mapped[
                "recommendation_id"
            ],
            action_type=mapped[
                "action_type"
            ],
            title=mapped[
                "title"
            ],
            description=mapped[
                "description"
            ],
            priority=mapped[
                "priority"
            ],
            evidence=evidence,
        )

        validate_recommendation(
            recommendation
        )

        recommendations.append(
            recommendation
        )

    return recommendations


def validate_generated_recommendations(
    recommendations: List[Dict[str, Any]],
) -> None:

    if not isinstance(
        recommendations,
        list,
    ):
        raise ValueError(
            "recommendations must be a list."
        )

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

        evidence = recommendation[
            "evidence"
        ]

        if not evidence.get(
            "source_factor_id"
        ):
            raise ValueError(
                f"Recommendation "
                f"{recommendation_id} is missing "
                f"source risk factor."
            )

        if not evidence.get(
            "source_event"
        ):
            raise ValueError(
                f"Recommendation "
                f"{recommendation_id} is missing "
                f"source event."
            )

        if not evidence.get(
            "source_artifact"
        ):
            raise ValueError(
                f"Recommendation "
                f"{recommendation_id} is missing "
                f"source artifact."
            )


if __name__ == "__main__":

    mapped_recommendations = [
        {
            "recommendation_id": "REC-001",
            "action_type":
                "PRESERVE_EVIDENCE",
            "title":
                "Preserve QR evidence",
            "description": (
                "Preserve the original artifact "
                "and recovered QR payload."
            ),
            "priority": "HIGH",
            "evidence": {
                "source_factor_id":
                    "RF-001",
                "source_event":
                    "EVENT-001",
                "source_artifact":
                    "event.ics",
                "mapping_method":
                    "RISK_TO_RECOMMENDATION",
            },
            "recommendation_status":
                "OBSERVED",
        }
    ]

    recommendations = (
        generate_recommendations(
            mapped_recommendations
        )
    )

    validate_generated_recommendations(
        recommendations
    )

    print(
        "EVIDENCE-BASED RECOMMENDATION "
        "GENERATION: PASS"
    )

    for recommendation in recommendations:
        print(
            recommendation[
                "recommendation_id"
            ],
            recommendation[
                "action_type"
            ],
            recommendation[
                "priority"
            ],
        )
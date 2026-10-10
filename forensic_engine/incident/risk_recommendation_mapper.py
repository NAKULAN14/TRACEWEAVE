"""
TRACEWEAVE - Phase 21.2
Risk to Response Recommendation Mapping
"""

from typing import Any, Dict, List


RISK_RECOMMENDATION_MAPPING = {
    "DELIVERY": [
        {
            "action_type": "REVIEW_EMAIL",
            "minimum_severity": "MEDIUM",
            "title": "Review suspicious email delivery",
            "description": (
                "Review the originating email, headers, "
                "recipients, and related messages."
            ),
        },
        {
            "action_type": "PRESERVE_EVIDENCE",
            "minimum_severity": "MEDIUM",
            "title": "Preserve email evidence",
            "description": (
                "Preserve the original email and "
                "associated metadata for investigation."
            ),
        },
    ],

    "USER_INTERACTION": [
        {
            "action_type": "REVIEW_USER_ACTIVITY",
            "minimum_severity": "HIGH",
            "title": "Review affected user activity",
            "description": (
                "Review available user and endpoint "
                "activity associated with the event."
            ),
        },
    ],

    "QR_EXPOSURE": [
        {
            "action_type": "PRESERVE_EVIDENCE",
            "minimum_severity": "MEDIUM",
            "title": "Preserve QR evidence",
            "description": (
                "Preserve the original artifact and "
                "recovered QR image or payload."
            ),
        },
        {
            "action_type": "DOCUMENT_FINDING",
            "minimum_severity": "MEDIUM",
            "title": "Document QR finding",
            "description": (
                "Document the recovered QR payload "
                "and its relationship to the source artifact."
            ),
        },
    ],

    "URL_EXPOSURE": [
        {
            "action_type": "BLOCK_IOC",
            "minimum_severity": "HIGH",
            "title": "Review URL for blocking",
            "description": (
                "Review the extracted URL for blocking "
                "across relevant security controls."
            ),
        },
        {
            "action_type": "PRESERVE_EVIDENCE",
            "minimum_severity": "MEDIUM",
            "title": "Preserve URL evidence",
            "description": (
                "Preserve the original and normalized "
                "URL together with its source artifact."
            ),
        },
    ],

    "IOC_EXPOSURE": [
        {
            "action_type": "BLOCK_IOC",
            "minimum_severity": "HIGH",
            "title": "Review IOC for blocking",
            "description": (
                "Review the observed IOC for blocking "
                "in applicable security controls."
            ),
        },
        {
            "action_type": "DOCUMENT_FINDING",
            "minimum_severity": "MEDIUM",
            "title": "Document observed IOC",
            "description": (
                "Document the IOC, source artifact, "
                "and observation provenance."
            ),
        },
    ],

    "INFRASTRUCTURE": [
        {
            "action_type": "MONITOR_INFRASTRUCTURE",
            "minimum_severity": "MEDIUM",
            "title": "Monitor identified infrastructure",
            "description": (
                "Monitor relevant domains, IP addresses, "
                "and other identified infrastructure."
            ),
        },
        {
            "action_type": "DOCUMENT_FINDING",
            "minimum_severity": "MEDIUM",
            "title": "Document infrastructure correlation",
            "description": (
                "Document observed DNS, IP, and TLS "
                "relationships without assuming ownership."
            ),
        },
    ],

    "CREDENTIAL_EXPOSURE": [
        {
            "action_type": "RESET_CREDENTIALS",
            "minimum_severity": "HIGH",
            "title": "Review credential reset requirement",
            "description": (
                "Review whether exposed credentials "
                "require reset or revocation."
            ),
        },
        {
            "action_type": "REVIEW_USER_ACTIVITY",
            "minimum_severity": "HIGH",
            "title": "Review authentication activity",
            "description": (
                "Review authentication and account activity "
                "associated with the affected identity."
            ),
        },
    ],

    "EXECUTION": [
        {
            "action_type": "INVESTIGATE_ENDPOINT",
            "minimum_severity": "HIGH",
            "title": "Investigate affected endpoint",
            "description": (
                "Perform endpoint investigation for "
                "evidence associated with the observed event."
            ),
        },
        {
            "action_type": "ISOLATE_ENDPOINT",
            "minimum_severity": "CRITICAL",
            "title": "Evaluate endpoint isolation",
            "description": (
                "Evaluate whether the affected endpoint "
                "should be isolated based on available evidence."
            ),
        },
    ],

    "DATA_EXPOSURE": [
        {
            "action_type": "INVESTIGATE_ENDPOINT",
            "minimum_severity": "HIGH",
            "title": "Investigate potential data exposure",
            "description": (
                "Investigate available endpoint and "
                "application evidence related to the exposure."
            ),
        },
    ],
}


SEVERITY_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def get_recommendations_for_risk(
    category: str,
    severity: str,
) -> List[Dict[str, Any]]:

    category = category.upper()
    severity = severity.upper()

    if category not in RISK_RECOMMENDATION_MAPPING:
        raise ValueError(
            f"Unsupported risk category: {category}"
        )

    if severity not in SEVERITY_ORDER:
        raise ValueError(
            f"Unsupported severity: {severity}"
        )

    current_level = SEVERITY_ORDER[
        severity
    ]

    recommendations = []

    for recommendation in (
        RISK_RECOMMENDATION_MAPPING[
            category
        ]
    ):

        minimum_level = SEVERITY_ORDER[
            recommendation[
                "minimum_severity"
            ]
        ]

        if current_level >= minimum_level:
            recommendations.append(
                recommendation
            )

    return recommendations


def map_risk_factors_to_recommendations(
    risk_factors: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        risk_factors,
        list,
    ):
        raise ValueError(
            "risk_factors must be a list."
        )

    recommendations = []
    recommendation_number = 1

    for factor in risk_factors:

        category = factor[
            "category"
        ]

        severity = factor[
            "severity"
        ]

        candidates = (
            get_recommendations_for_risk(
                category,
                severity,
            )
        )

        for candidate in candidates:

            recommendation = {
                "recommendation_id":
                    f"REC-{recommendation_number:03d}",
                "action_type":
                    candidate["action_type"],
                "title":
                    candidate["title"],
                "description":
                    candidate["description"],
                "priority":
                    severity,
                "evidence": {
                    "source_factor_id":
                        factor["factor_id"],
                    "source_event":
                        factor["evidence"][
                            "source_event"
                        ],
                    "source_artifact":
                        factor["evidence"][
                            "source_artifact"
                        ],
                    "mapping_method":
                        "RISK_TO_RECOMMENDATION",
                },
                "recommendation_status":
                    "OBSERVED",
            }

            recommendations.append(
                recommendation
            )

            recommendation_number += 1

    return recommendations


def validate_risk_recommendation_mapping(
    recommendation: Dict[str, Any],
) -> None:

    required_fields = {
        "recommendation_id",
        "action_type",
        "title",
        "description",
        "priority",
        "evidence",
        "recommendation_status",
    }

    missing = (
        required_fields
        - set(recommendation.keys())
    )

    if missing:
        raise ValueError(
            "Recommendation mapping missing "
            f"fields: {sorted(missing)}"
        )

    evidence = recommendation[
        "evidence"
    ]

    if not evidence.get(
        "source_factor_id"
    ):
        raise ValueError(
            "Recommendation must reference "
            "a source risk factor."
        )

    if not evidence.get(
        "source_event"
    ):
        raise ValueError(
            "Recommendation must reference "
            "a source event."
        )

    if not evidence.get(
        "source_artifact"
    ):
        raise ValueError(
            "Recommendation must reference "
            "a source artifact."
        )

    if recommendation[
        "recommendation_status"
    ] != "OBSERVED":

        raise ValueError(
            "Recommendation status must "
            "remain OBSERVED."
        )


if __name__ == "__main__":

    test_factors = [
        {
            "factor_id": "RF-001",
            "category": "QR_EXPOSURE",
            "severity": "HIGH",
            "evidence": {
                "source_event": "EVENT-001",
                "source_artifact": "event.ics",
            },
        },
        {
            "factor_id": "RF-002",
            "category": "URL_EXPOSURE",
            "severity": "HIGH",
            "evidence": {
                "source_event": "EVENT-002",
                "source_artifact": "qr.png",
            },
        },
    ]

    recommendations = (
        map_risk_factors_to_recommendations(
            test_factors
        )
    )

    for recommendation in recommendations:
        validate_risk_recommendation_mapping(
            recommendation
        )

    print(
        "RISK → RECOMMENDATION MAPPING: PASS"
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
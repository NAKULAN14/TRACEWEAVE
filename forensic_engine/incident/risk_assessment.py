"""
TRACEWEAVE - Phase 20.4
Risk Assessment Construction
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.incident.risk_factor import (
    validate_risk_factor,
)

from forensic_engine.incident.risk_scorer import (
    calculate_risk_score,
    validate_risk_score,
)


def build_risk_assessment(
    case_id: str,
    risk_factors: List[Dict[str, Any]],
) -> Dict[str, Any]:

    if not isinstance(
        case_id,
        str,
    ) or not case_id.strip():

        raise ValueError(
            "case_id must be a non-empty string."
        )

    if not isinstance(
        risk_factors,
        list,
    ):

        raise ValueError(
            "risk_factors must be a list."
        )

    # Validate every risk factor first.
    for factor in risk_factors:
        validate_risk_factor(
            factor
        )

    # Calculate deterministic risk score.
    score = calculate_risk_score(
        risk_factors
    )

    validate_risk_score(
        score
    )

    assessment = {
        "risk_assessment_id":
            f"RISK-{case_id}",
        "case_id":
            case_id,
        "assessment_type":
            "TRACEWEAVE_FORENSIC_RISK_ASSESSMENT",
        "schema_version":
            "1.0",
        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "assessment_status":
            "OBSERVED",
        "risk_level":
            score["risk_level"],
        "total_score":
            score["total_score"],
        "factor_count":
            len(risk_factors),
        "risk_factors":
            risk_factors,
        "score_breakdown":
            score["factor_scores"],
        "scoring_method":
            score["scoring_method"],
        "provenance": {
            "construction_method":
                "RISK_FACTOR_AGGREGATION",
            "evidence_basis":
                "OBSERVED",
            "network_access_performed":
                False,
        },
    }

    validate_risk_assessment(
        assessment
    )

    return assessment


def validate_risk_assessment(
    assessment: Dict[str, Any],
) -> None:

    required_fields = {
        "risk_assessment_id",
        "case_id",
        "assessment_type",
        "schema_version",
        "created_at",
        "assessment_status",
        "risk_level",
        "total_score",
        "factor_count",
        "risk_factors",
        "score_breakdown",
        "scoring_method",
        "provenance",
    }

    missing = (
        required_fields
        - set(assessment.keys())
    )

    if missing:
        raise ValueError(
            "Risk assessment missing fields: "
            f"{sorted(missing)}"
        )

    if assessment[
        "assessment_type"
    ] != "TRACEWEAVE_FORENSIC_RISK_ASSESSMENT":

        raise ValueError(
            "Invalid risk assessment type."
        )

    if assessment[
        "schema_version"
    ] != "1.0":

        raise ValueError(
            "Unsupported risk assessment schema."
        )

    if assessment[
        "assessment_status"
    ] != "OBSERVED":

        raise ValueError(
            "Assessment status must remain OBSERVED."
        )

    if assessment[
        "risk_level"
    ] not in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }:

        raise ValueError(
            "Invalid risk level."
        )

    risk_factors = assessment[
        "risk_factors"
    ]

    if not isinstance(
        risk_factors,
        list,
    ):

        raise ValueError(
            "risk_factors must be a list."
        )

    if assessment[
        "factor_count"
    ] != len(risk_factors):

        raise ValueError(
            "factor_count does not match "
            "risk factor count."
        )

    factor_ids = set()

    for factor in risk_factors:

        validate_risk_factor(
            factor
        )

        factor_id = factor[
            "factor_id"
        ]

        if factor_id in factor_ids:
            raise ValueError(
                f"Duplicate risk factor: "
                f"{factor_id}"
            )

        factor_ids.add(
            factor_id
        )

    score_breakdown = assessment[
        "score_breakdown"
    ]

    if len(score_breakdown) != (
        len(risk_factors)
    ):
        raise ValueError(
            "Score breakdown count does not "
            "match risk-factor count."
        )

    breakdown_ids = {
        item["factor_id"]
        for item in score_breakdown
    }

    if breakdown_ids != factor_ids:
        raise ValueError(
            "Score breakdown does not "
            "match risk factors."
        )

    calculated_total = sum(
        item["score"]
        for item in score_breakdown
    )

    if calculated_total != (
        assessment["total_score"]
    ):
        raise ValueError(
            "Total risk score is inconsistent."
        )

    provenance = assessment[
        "provenance"
    ]

    if not isinstance(
        provenance,
        dict,
    ):
        raise ValueError(
            "Risk assessment provenance "
            "must be an object."
        )

    if provenance.get(
        "evidence_basis"
    ) != "OBSERVED":

        raise ValueError(
            "Risk assessment evidence basis "
            "must be OBSERVED."
        )

    if provenance.get(
        "network_access_performed"
    ) is not False:

        raise ValueError(
            "Risk assessment must not indicate "
            "network access."
        )


if __name__ == "__main__":

    from forensic_engine.incident.risk_factor import (
        create_risk_factor,
    )

    factors = [
        create_risk_factor(
            "RF-001",
            "QR_EXPOSURE",
            "A QR code was recovered.",
            "MEDIUM",
            {
                "source_event":
                    "EVENT-001",
                "source_artifact":
                    "event.ics",
            },
        ),
        create_risk_factor(
            "RF-002",
            "URL_EXPOSURE",
            "A URL was extracted.",
            "HIGH",
            {
                "source_event":
                    "EVENT-002",
                "source_artifact":
                    "event.ics",
            },
        ),
    ]

    assessment = build_risk_assessment(
        "TW-TEST-001",
        factors,
    )

    validate_risk_assessment(
        assessment
    )

    print(
        "RISK ASSESSMENT CONSTRUCTION: PASS"
    )

    print(
        f"Risk level: "
        f"{assessment['risk_level']}"
    )

    print(
        f"Total score: "
        f"{assessment['total_score']}"
    )
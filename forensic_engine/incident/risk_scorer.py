"""
TRACEWEAVE - Phase 20.3
Risk Scoring
"""

from typing import Any, Dict, List


SEVERITY_SCORES = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def score_risk_factor(
    factor: Dict[str, Any],
) -> int:

    if not isinstance(
        factor,
        dict,
    ):
        raise ValueError(
            "Risk factor must be a dictionary."
        )

    severity = factor.get(
        "severity"
    )

    if severity not in SEVERITY_SCORES:
        raise ValueError(
            f"Unsupported severity: {severity}"
        )

    return SEVERITY_SCORES[
        severity
    ]


def calculate_risk_score(
    factors: List[Dict[str, Any]],
) -> Dict[str, Any]:

    if not isinstance(
        factors,
        list,
    ):
        raise ValueError(
            "Risk factors must be a list."
        )

    factor_scores = []

    for factor in factors:

        score = score_risk_factor(
            factor
        )

        factor_scores.append({
            "factor_id":
                factor["factor_id"],
            "severity":
                factor["severity"],
            "score":
                score,
        })

    total_score = sum(
        item["score"]
        for item in factor_scores
    )

    if total_score <= 3:
        risk_level = "LOW"

    elif total_score <= 6:
        risk_level = "MEDIUM"

    elif total_score <= 9:
        risk_level = "HIGH"

    else:
        risk_level = "CRITICAL"

    return {
        "total_score":
            total_score,
        "risk_level":
            risk_level,
        "factor_count":
            len(factors),
        "factor_scores":
            factor_scores,
        "scoring_method":
            "SEVERITY_SUM",
    }


def validate_risk_score(
    result: Dict[str, Any],
) -> None:

    required_fields = {
        "total_score",
        "risk_level",
        "factor_count",
        "factor_scores",
        "scoring_method",
    }

    missing = (
        required_fields
        - set(result.keys())
    )

    if missing:
        raise ValueError(
            "Risk score missing fields: "
            f"{sorted(missing)}"
        )

    if result[
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

    if not isinstance(
        result["total_score"],
        int,
    ):
        raise ValueError(
            "Total score must be an integer."
        )

    if result[
        "total_score"
    ] < 0:

        raise ValueError(
            "Total score cannot be negative."
        )

    if result[
        "factor_count"
    ] != len(
        result["factor_scores"]
    ):

        raise ValueError(
            "Factor count does not match "
            "factor-score count."
        )

    calculated_total = sum(
        item["score"]
        for item in result[
            "factor_scores"
        ]
    )

    if calculated_total != (
        result["total_score"]
    ):

        raise ValueError(
            "Risk score total is inconsistent."
        )


if __name__ == "__main__":

    test_factors = [
        {
            "factor_id": "RF-001",
            "severity": "MEDIUM",
        },
        {
            "factor_id": "RF-002",
            "severity": "HIGH",
        },
        {
            "factor_id": "RF-003",
            "severity": "HIGH",
        },
    ]

    result = calculate_risk_score(
        test_factors
    )

    validate_risk_score(
        result
    )

    print(
        "RISK SCORING: PASS"
    )

    print(
        f"Total score: "
        f"{result['total_score']}"
    )

    print(
        f"Risk level: "
        f"{result['risk_level']}"
    )
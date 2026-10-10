"""
TRACEWEAVE - Phase 20.6
Risk Assessment Validation
"""

from typing import Any, Dict

from forensic_engine.incident.risk_assessment import (
    validate_risk_assessment,
)

from forensic_engine.incident.risk_assessment_provenance import (
    validate_risk_assessment_provenance,
)


def validate_complete_risk_assessment(
    assessment: Dict[str, Any],
) -> None:

    # ---------------------------------------------
    # Base assessment validation
    # ---------------------------------------------

    validate_risk_assessment(
        assessment
    )

    risk_factors = assessment[
        "risk_factors"
    ]

    factor_ids = {
        factor["factor_id"]
        for factor in risk_factors
    }

    # ---------------------------------------------
    # Risk-factor evidence validation
    # ---------------------------------------------

    for factor in risk_factors:

        evidence = factor.get(
            "evidence"
        )

        if not isinstance(
            evidence,
            dict,
        ):
            raise ValueError(
                f"Risk factor "
                f"{factor['factor_id']} "
                f"has invalid evidence."
            )

        if not evidence.get(
            "source_event"
        ):
            raise ValueError(
                f"Risk factor "
                f"{factor['factor_id']} "
                f"is missing source event."
            )

        if not evidence.get(
            "source_artifact"
        ):
            raise ValueError(
                f"Risk factor "
                f"{factor['factor_id']} "
                f"is missing source artifact."
            )

        if factor.get(
            "assessment_status"
        ) != "OBSERVED":

            raise ValueError(
                f"Risk factor "
                f"{factor['factor_id']} "
                f"must be OBSERVED."
            )

    # ---------------------------------------------
    # Score breakdown consistency
    # ---------------------------------------------

    score_breakdown = assessment[
        "score_breakdown"
    ]

    breakdown_ids = {
        item["factor_id"]
        for item in score_breakdown
    }

    if breakdown_ids != factor_ids:
        raise ValueError(
            "Score breakdown factor IDs do not "
            "match risk-factor IDs."
        )

    total_score = sum(
        item["score"]
        for item in score_breakdown
    )

    if total_score != assessment[
        "total_score"
    ]:
        raise ValueError(
            "Risk score does not match "
            "score breakdown."
        )

    # ---------------------------------------------
    # Risk-level consistency
    # ---------------------------------------------

    if total_score <= 3:
        expected_level = "LOW"

    elif total_score <= 6:
        expected_level = "MEDIUM"

    elif total_score <= 9:
        expected_level = "HIGH"

    else:
        expected_level = "CRITICAL"

    if assessment[
        "risk_level"
    ] != expected_level:

        raise ValueError(
            "Risk level does not match "
            "the configured scoring thresholds."
        )

    # ---------------------------------------------
    # Assessment provenance
    # ---------------------------------------------

    provenance = assessment.get(
        "assessment_provenance"
    )

    if provenance is not None:

        validate_risk_assessment_provenance(
            provenance
        )

        provenance_factor_ids = set(
            provenance[
                "source_factor_ids"
            ]
        )

        if not provenance_factor_ids.issubset(
            factor_ids
        ):
            raise ValueError(
                "Risk-assessment provenance "
                "references an unknown risk factor."
            )

    # ---------------------------------------------
    # Base provenance
    # ---------------------------------------------

    base_provenance = assessment[
        "provenance"
    ]

    if base_provenance.get(
        "evidence_basis"
    ) != "OBSERVED":

        raise ValueError(
            "Risk assessment evidence basis "
            "must be OBSERVED."
        )

    if base_provenance.get(
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

    from forensic_engine.incident.risk_assessment import (
        build_risk_assessment,
    )

    from forensic_engine.incident.risk_assessment_provenance import (
        create_risk_assessment_provenance,
        attach_risk_provenance,
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

    provenance = (
        create_risk_assessment_provenance(
            derivation_type=
                "RISK_SCORE_AGGREGATION",
            source_factor_ids=[
                "RF-001",
                "RF-002",
            ],
            scoring_method=
                "SEVERITY_SUM",
            explanation=(
                "The risk assessment was derived "
                "from the observed risk factors."
            ),
        )
    )

    attach_risk_provenance(
        assessment,
        provenance,
    )

    validate_complete_risk_assessment(
        assessment
    )

    print(
        "RISK ASSESSMENT VALIDATION: PASS"
    )
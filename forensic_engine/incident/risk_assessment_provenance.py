"""
TRACEWEAVE - Phase 20.5
Risk Assessment Provenance
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_DERIVATION_TYPES = {
    "EVIDENCE_TO_RISK_FACTOR",
    "RISK_FACTOR_SCORING",
    "RISK_SCORE_AGGREGATION",
}


def create_risk_assessment_provenance(
    derivation_type: str,
    source_factor_ids: list,
    scoring_method: str,
    explanation: str,
) -> Dict[str, Any]:

    derivation_type = derivation_type.upper()

    if derivation_type not in (
        SUPPORTED_DERIVATION_TYPES
    ):
        raise ValueError(
            f"Unsupported derivation type: "
            f"{derivation_type}"
        )

    if not isinstance(
        source_factor_ids,
        list,
    ) or not source_factor_ids:

        raise ValueError(
            "source_factor_ids must be a "
            "non-empty list."
        )

    if not scoring_method:
        raise ValueError(
            "scoring_method is required."
        )

    if not explanation:
        raise ValueError(
            "explanation is required."
        )

    return {
        "derivation_type":
            derivation_type,
        "source_factor_ids":
            source_factor_ids,
        "scoring_method":
            scoring_method,
        "explanation":
            explanation,
        "assessment_status":
            "OBSERVED",
        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "network_access_performed":
            False,
    }


def attach_risk_provenance(
    assessment: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        assessment,
        dict,
    ):
        raise ValueError(
            "assessment must be a dictionary."
        )

    if not isinstance(
        provenance,
        dict,
    ):
        raise ValueError(
            "provenance must be a dictionary."
        )

    assessment[
        "assessment_provenance"
    ] = provenance

    return assessment


def validate_risk_assessment_provenance(
    provenance: Dict[str, Any],
) -> None:

    required_fields = {
        "derivation_type",
        "source_factor_ids",
        "scoring_method",
        "explanation",
        "assessment_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(provenance.keys())
    )

    if missing:
        raise ValueError(
            "Risk-assessment provenance missing "
            f"fields: {sorted(missing)}"
        )

    if provenance[
        "derivation_type"
    ] not in SUPPORTED_DERIVATION_TYPES:

        raise ValueError(
            "Unsupported derivation type."
        )

    if not provenance[
        "source_factor_ids"
    ]:

        raise ValueError(
            "At least one source risk factor "
            "is required."
        )

    if not provenance[
        "scoring_method"
    ]:

        raise ValueError(
            "Scoring method cannot be empty."
        )

    if not provenance[
        "explanation"
    ]:

        raise ValueError(
            "Explanation cannot be empty."
        )

    if provenance[
        "assessment_status"
    ] != "OBSERVED":

        raise ValueError(
            "Assessment status must remain OBSERVED."
        )

    if provenance[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "Risk-assessment provenance must "
            "not perform network access."
        )


if __name__ == "__main__":

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
                "The case-level risk assessment "
                "was derived by aggregating the "
                "scores of the observed risk factors."
            ),
        )
    )

    validate_risk_assessment_provenance(
        provenance
    )

    print(
        "RISK ASSESSMENT PROVENANCE: PASS"
    )
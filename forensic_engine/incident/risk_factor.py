"""
TRACEWEAVE - Phase 20.1
Risk Factor Model
"""

from typing import Any, Dict


SUPPORTED_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


SUPPORTED_RISK_CATEGORIES = {
    "DELIVERY",
    "USER_INTERACTION",
    "QR_EXPOSURE",
    "URL_EXPOSURE",
    "IOC_EXPOSURE",
    "INFRASTRUCTURE",
    "CREDENTIAL_EXPOSURE",
    "EXECUTION",
    "DATA_EXPOSURE",
}


def create_risk_factor(
    factor_id: str,
    category: str,
    description: str,
    severity: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        factor_id,
        str,
    ) or not factor_id.strip():

        raise ValueError(
            "factor_id must be a "
            "non-empty string."
        )

    category = category.upper()

    if category not in (
        SUPPORTED_RISK_CATEGORIES
    ):
        raise ValueError(
            f"Unsupported risk category: "
            f"{category}"
        )

    severity = severity.upper()

    if severity not in (
        SUPPORTED_RISK_LEVELS
    ):
        raise ValueError(
            f"Unsupported risk level: "
            f"{severity}"
        )

    if not isinstance(
        description,
        str,
    ) or not description.strip():

        raise ValueError(
            "description must be a "
            "non-empty string."
        )

    if not isinstance(
        evidence,
        dict,
    ):

        raise ValueError(
            "evidence must be a dictionary."
        )

    return {
        "factor_id": factor_id.strip(),
        "category": category,
        "description": description.strip(),
        "severity": severity,
        "evidence": evidence,
        "assessment_status": "OBSERVED",
    }


def validate_risk_factor(
    factor: Dict[str, Any],
) -> None:

    required_fields = {
        "factor_id",
        "category",
        "description",
        "severity",
        "evidence",
        "assessment_status",
    }

    missing = (
        required_fields
        - set(factor.keys())
    )

    if missing:
        raise ValueError(
            "Risk factor missing fields: "
            f"{sorted(missing)}"
        )

    if factor[
        "category"
    ] not in SUPPORTED_RISK_CATEGORIES:

        raise ValueError(
            "Unsupported risk category."
        )

    if factor[
        "severity"
    ] not in SUPPORTED_RISK_LEVELS:

        raise ValueError(
            "Unsupported risk level."
        )

    if not isinstance(
        factor["evidence"],
        dict,
    ):

        raise ValueError(
            "Risk-factor evidence must "
            "be a dictionary."
        )

    if factor[
        "assessment_status"
    ] != "OBSERVED":

        raise ValueError(
            "Assessment status must remain OBSERVED."
        )
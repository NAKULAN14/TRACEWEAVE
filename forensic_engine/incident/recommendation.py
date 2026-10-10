"""
TRACEWEAVE - Phase 21.1
Response Recommendation Model
"""

from typing import Any, Dict


SUPPORTED_PRIORITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


SUPPORTED_ACTION_TYPES = {
    "PRESERVE_EVIDENCE",
    "BLOCK_IOC",
    "INVESTIGATE_ENDPOINT",
    "REVIEW_USER_ACTIVITY",
    "RESET_CREDENTIALS",
    "ISOLATE_ENDPOINT",
    "MONITOR_INFRASTRUCTURE",
    "REVIEW_EMAIL",
    "DOCUMENT_FINDING",
}


def create_recommendation(
    recommendation_id: str,
    action_type: str,
    title: str,
    description: str,
    priority: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        recommendation_id,
        str,
    ) or not recommendation_id.strip():

        raise ValueError(
            "recommendation_id must be "
            "a non-empty string."
        )

    action_type = action_type.upper()

    if action_type not in (
        SUPPORTED_ACTION_TYPES
    ):
        raise ValueError(
            f"Unsupported action type: "
            f"{action_type}"
        )

    if not isinstance(
        title,
        str,
    ) or not title.strip():

        raise ValueError(
            "title must be a "
            "non-empty string."
        )

    if not isinstance(
        description,
        str,
    ) or not description.strip():

        raise ValueError(
            "description must be a "
            "non-empty string."
        )

    priority = priority.upper()

    if priority not in (
        SUPPORTED_PRIORITIES
    ):
        raise ValueError(
            f"Unsupported priority: "
            f"{priority}"
        )

    if not isinstance(
        evidence,
        dict,
    ):

        raise ValueError(
            "evidence must be a dictionary."
        )

    return {
        "recommendation_id":
            recommendation_id.strip(),
        "action_type":
            action_type,
        "title":
            title.strip(),
        "description":
            description.strip(),
        "priority":
            priority,
        "evidence":
            evidence,
        "recommendation_status":
            "OBSERVED",
    }


def validate_recommendation(
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
            "Recommendation missing fields: "
            f"{sorted(missing)}"
        )

    if recommendation[
        "action_type"
    ] not in SUPPORTED_ACTION_TYPES:

        raise ValueError(
            "Unsupported action type."
        )

    if recommendation[
        "priority"
    ] not in SUPPORTED_PRIORITIES:

        raise ValueError(
            "Unsupported recommendation priority."
        )

    if not isinstance(
        recommendation["evidence"],
        dict,
    ):

        raise ValueError(
            "Recommendation evidence must "
            "be a dictionary."
        )

    if recommendation[
        "recommendation_status"
    ] != "OBSERVED":

        raise ValueError(
            "Recommendation status must "
            "remain OBSERVED."
        )
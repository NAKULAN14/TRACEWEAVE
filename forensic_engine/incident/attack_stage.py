"""
TRACEWEAVE - Phase 18.1
Attack Stage Model
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_ATTACK_STAGES = {
    "DELIVERY",
    "ARTIFACT_INTERACTION",
    "QR_DISCOVERY",
    "QR_DECODE",
    "URL_EXTRACTION",
    "IOC_EXTRACTION",
    "INFRASTRUCTURE_CORRELATION",
}


STAGE_ORDER = {
    "DELIVERY": 1,
    "ARTIFACT_INTERACTION": 2,
    "QR_DISCOVERY": 3,
    "QR_DECODE": 4,
    "URL_EXTRACTION": 5,
    "IOC_EXTRACTION": 6,
    "INFRASTRUCTURE_CORRELATION": 7,
}


def create_attack_stage(
    stage_type: str,
    sequence_number: int,
    description: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    stage_type = stage_type.upper()

    if stage_type not in SUPPORTED_ATTACK_STAGES:
        raise ValueError(
            f"Unsupported attack stage: {stage_type}"
        )

    if not isinstance(
        sequence_number,
        int,
    ) or sequence_number < 1:

        raise ValueError(
            "sequence_number must be a "
            "positive integer."
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
        "stage_id": (
            f"STAGE-{sequence_number}-"
            f"{stage_type}"
        ),
        "stage_type": stage_type,
        "sequence_number": sequence_number,
        "description": description.strip(),
        "evidence": evidence,
        "stage_status": "OBSERVED",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def validate_attack_stage(
    stage: Dict[str, Any],
) -> None:

    required_fields = {
        "stage_id",
        "stage_type",
        "sequence_number",
        "description",
        "evidence",
        "stage_status",
        "created_at",
    }

    missing = (
        required_fields
        - set(stage.keys())
    )

    if missing:
        raise ValueError(
            "Attack stage missing fields: "
            f"{sorted(missing)}"
        )

    stage_type = stage[
        "stage_type"
    ]

    if stage_type not in (
        SUPPORTED_ATTACK_STAGES
    ):
        raise ValueError(
            f"Unsupported attack stage: {stage_type}"
        )

    sequence_number = stage[
        "sequence_number"
    ]

    if not isinstance(
        sequence_number,
        int,
    ) or sequence_number < 1:

        raise ValueError(
            "Invalid stage sequence number."
        )

    expected_id = (
        f"STAGE-{sequence_number}-"
        f"{stage_type}"
    )

    if stage[
        "stage_id"
    ] != expected_id:

        raise ValueError(
            "Attack stage ID does not match "
            "sequence number and stage type."
        )

    if stage[
        "stage_status"
    ] != "OBSERVED":

        raise ValueError(
            "Attack stage status must remain OBSERVED."
        )

    if not isinstance(
        stage["evidence"],
        dict,
    ):
        raise ValueError(
            "Attack stage evidence must be an object."
        )
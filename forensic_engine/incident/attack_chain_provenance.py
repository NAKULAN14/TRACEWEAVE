"""
TRACEWEAVE - Phase 18.5
Attack Chain Provenance
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_PROVENANCE_TYPES = {
    "TIMELINE_EVENT_MAPPING",
    "ARTIFACT_OBSERVATION",
    "QR_EXTRACTION",
    "IOC_OBSERVATION",
    "INFRASTRUCTURE_CORRELATION",
}


def create_attack_chain_provenance(
    provenance_type: str,
    source_event: str,
    source_artifact: str,
    source_location: str,
    explanation: str,
) -> Dict[str, Any]:

    provenance_type = provenance_type.upper()

    if provenance_type not in (
        SUPPORTED_PROVENANCE_TYPES
    ):
        raise ValueError(
            f"Unsupported provenance type: "
            f"{provenance_type}"
        )

    if not source_event:
        raise ValueError(
            "source_event is required."
        )

    if not source_artifact:
        raise ValueError(
            "source_artifact is required."
        )

    if not explanation:
        raise ValueError(
            "explanation is required."
        )

    return {
        "provenance_type":
            provenance_type,
        "source_event":
            source_event,
        "source_artifact":
            source_artifact,
        "source_location":
            source_location,
        "explanation":
            explanation,
        "derivation_status":
            "OBSERVED",
        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "network_access_performed":
            False,
    }


def attach_stage_provenance(
    stage: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        stage,
        dict,
    ):
        raise ValueError(
            "stage must be a dictionary."
        )

    if not isinstance(
        provenance,
        dict,
    ):
        raise ValueError(
            "provenance must be a dictionary."
        )

    stage["provenance"] = provenance

    return stage


def validate_attack_chain_provenance(
    provenance: Dict[str, Any],
) -> None:

    required_fields = {
        "provenance_type",
        "source_event",
        "source_artifact",
        "source_location",
        "explanation",
        "derivation_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(provenance.keys())
    )

    if missing:
        raise ValueError(
            "Attack-chain provenance missing "
            f"fields: {sorted(missing)}"
        )

    if provenance[
        "provenance_type"
    ] not in SUPPORTED_PROVENANCE_TYPES:

        raise ValueError(
            "Unsupported provenance type."
        )

    if provenance[
        "derivation_status"
    ] != "OBSERVED":

        raise ValueError(
            "Derivation status must remain OBSERVED."
        )

    if provenance[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "Attack-chain provenance must "
            "not perform network access."
        )

    if not provenance[
        "source_event"
    ]:

        raise ValueError(
            "source_event cannot be empty."
        )

    if not provenance[
        "source_artifact"
    ]:

        raise ValueError(
            "source_artifact cannot be empty."
        )

    if not provenance[
        "explanation"
    ]:

        raise ValueError(
            "explanation cannot be empty."
        )   
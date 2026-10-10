"""
TRACEWEAVE - Phase 16.5
Incident Reconstruction Provenance
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_DERIVATION_TYPES = {
    "DIRECT_OBSERVATION",
    "ARTIFACT_LINK",
    "IOC_EXTRACTION",
    "INFRASTRUCTURE_CORRELATION",
    "CROSS_LAYER_CORRELATION",
}


def create_reconstruction_provenance(
    derivation_type: str,
    source_evidence: str,
    source_artifact: str = None,
    source_location: str = None,
    explanation: str = "",
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
        source_evidence,
        str,
    ) or not source_evidence.strip():

        raise ValueError(
            "source_evidence must be a "
            "non-empty string."
        )

    if source_artifact is not None:
        source_artifact = (
            source_artifact.strip()
        )

    if source_location is not None:
        source_location = (
            source_location.strip()
        )

    return {
        "derivation_type": derivation_type,
        "source_evidence": (
            source_evidence.strip()
        ),
        "source_artifact": source_artifact,
        "source_location": source_location,
        "explanation": explanation,
        "relationship_status": "OBSERVED",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "network_access_performed": False,
    }


def attach_provenance(
    reconstruction: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        reconstruction,
        dict,
    ):
        raise ValueError(
            "Reconstruction must be a dictionary."
        )

    if not isinstance(
        provenance,
        dict,
    ):
        raise ValueError(
            "Provenance must be a dictionary."
        )

    reconstruction = dict(
        reconstruction
    )

    reconstruction[
        "provenance"
    ] = provenance

    return reconstruction


def validate_reconstruction_provenance(
    provenance: Dict[str, Any],
) -> None:

    required_fields = {
        "derivation_type",
        "source_evidence",
        "source_artifact",
        "source_location",
        "explanation",
        "relationship_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(provenance.keys())
    )

    if missing:
        raise ValueError(
            "Reconstruction provenance missing "
            f"fields: {sorted(missing)}"
        )

    if provenance[
        "derivation_type"
    ] not in SUPPORTED_DERIVATION_TYPES:

        raise ValueError(
            "Invalid reconstruction derivation type."
        )

    if not provenance[
        "source_evidence"
    ]:

        raise ValueError(
            "source_evidence cannot be empty."
        )

    if provenance[
        "relationship_status"
    ] != "OBSERVED":

        raise ValueError(
            "Reconstruction provenance must "
            "remain OBSERVED."
        )

    if provenance[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "Reconstruction provenance must "
            "record network access as false."
        )
"""
TRACEWEAVE - Phase 19.5
MITRE ATT&CK Mapping Provenance
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_DERIVATION_TYPES = {
    "STAGE_TO_TECHNIQUE_MAPPING",
    "TECHNIQUE_EVIDENCE_CORRELATION",
    "TIMELINE_EVIDENCE_CORRELATION",
}


def create_attack_mapping_provenance(
    derivation_type: str,
    technique_id: str,
    source_stage: str,
    source_event: str,
    source_artifact: str,
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

    if not technique_id:
        raise ValueError(
            "technique_id is required."
        )

    if not source_stage:
        raise ValueError(
            "source_stage is required."
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
        "derivation_type":
            derivation_type,
        "technique_id":
            technique_id,
        "source_stage":
            source_stage,
        "source_event":
            source_event,
        "source_artifact":
            source_artifact,
        "explanation":
            explanation,
        "mapping_status":
            "OBSERVED",
        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "network_access_performed":
            False,
    }


def attach_mapping_provenance(
    mapping: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        mapping,
        dict,
    ):
        raise ValueError(
            "mapping must be a dictionary."
        )

    if not isinstance(
        provenance,
        dict,
    ):
        raise ValueError(
            "provenance must be a dictionary."
        )

    mapping[
        "provenance"
    ] = provenance

    return mapping


def validate_attack_mapping_provenance(
    provenance: Dict[str, Any],
) -> None:

    required_fields = {
        "derivation_type",
        "technique_id",
        "source_stage",
        "source_event",
        "source_artifact",
        "explanation",
        "mapping_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(provenance.keys())
    )

    if missing:
        raise ValueError(
            "ATT&CK mapping provenance missing "
            f"fields: {sorted(missing)}"
        )

    if provenance[
        "derivation_type"
    ] not in SUPPORTED_DERIVATION_TYPES:

        raise ValueError(
            "Unsupported derivation type."
        )

    for field in (
        "technique_id",
        "source_stage",
        "source_event",
        "source_artifact",
        "explanation",
    ):
        if not provenance.get(field):
            raise ValueError(
                f"{field} cannot be empty."
            )

    if provenance[
        "mapping_status"
    ] != "OBSERVED":

        raise ValueError(
            "Mapping status must remain OBSERVED."
        )

    if provenance[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "ATT&CK mapping provenance must "
            "not perform network access."
        )


if __name__ == "__main__":

    provenance = create_attack_mapping_provenance(
        derivation_type=(
            "TECHNIQUE_EVIDENCE_CORRELATION"
        ),
        technique_id="T1566.001",
        source_stage="DELIVERY",
        source_event="EVENT-001",
        source_artifact="email.eml",
        explanation=(
            "The ATT&CK technique mapping is "
            "derived from the observed delivery "
            "stage and its supporting evidence."
        ),
    )

    validate_attack_mapping_provenance(
        provenance
    )

    print(
        "ATT&CK MAPPING PROVENANCE: PASS"
    )
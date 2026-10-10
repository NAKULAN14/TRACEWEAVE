"""
TRACEWEAVE - Phase 18.4
Attack Chain Construction
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.incident.attack_stage import (
    validate_attack_stage,
)
from forensic_engine.incident.stage_orderer import (
    order_attack_stages,
    validate_stage_order,
)


def build_attack_chain(
    case_id: str,
    stages: List[Dict[str, Any]],
) -> Dict[str, Any]:

    if not isinstance(
        case_id,
        str,
    ) or not case_id.strip():

        raise ValueError(
            "case_id must be a non-empty string."
        )

    if not isinstance(
        stages,
        list,
    ):

        raise ValueError(
            "stages must be a list."
        )

    # Validate each stage before construction.
    for stage in stages:
        validate_attack_stage(stage)

    # Put stages into logical attack order.
    ordered_stages = order_attack_stages(
        stages
    )

    validate_stage_order(
        ordered_stages
    )

    chain = {
        "attack_chain_id": (
            f"AC-{case_id}"
        ),
        "case_id": case_id,
        "chain_type":
            "TRACEWEAVE_ATTACK_CHAIN",
        "schema_version": "1.0",
        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "chain_status":
            "OBSERVED",
        "stage_count":
            len(ordered_stages),
        "stages":
            ordered_stages,
        "provenance": {
            "construction_method":
                "TIMELINE_TO_ATTACK_STAGE_MAPPING",
            "evidence_basis":
                "OBSERVED",
            "network_access_performed":
                False,
        },
    }

    validate_attack_chain(
        chain
    )

    return chain


def validate_attack_chain(
    chain: Dict[str, Any],
) -> None:

    required_fields = {
        "attack_chain_id",
        "case_id",
        "chain_type",
        "schema_version",
        "created_at",
        "chain_status",
        "stage_count",
        "stages",
        "provenance",
    }

    missing = (
        required_fields
        - set(chain.keys())
    )

    if missing:
        raise ValueError(
            "Attack chain missing fields: "
            f"{sorted(missing)}"
        )

    if chain[
        "chain_type"
    ] != "TRACEWEAVE_ATTACK_CHAIN":

        raise ValueError(
            "Invalid attack chain type."
        )

    if chain[
        "schema_version"
    ] != "1.0":

        raise ValueError(
            "Unsupported attack chain schema version."
        )

    if chain[
        "chain_status"
    ] != "OBSERVED":

        raise ValueError(
            "Attack chain status must remain OBSERVED."
        )

    stages = chain[
        "stages"
    ]

    if not isinstance(
        stages,
        list,
    ):

        raise ValueError(
            "Attack chain stages must be a list."
        )

    if chain[
        "stage_count"
    ] != len(stages):

        raise ValueError(
            "Attack chain stage count does not "
            "match actual stage count."
        )

    validate_stage_order(
        stages
    )

    stage_ids = [
        stage["stage_id"]
        for stage in stages
    ]

    if len(stage_ids) != len(
        set(stage_ids)
    ):

        raise ValueError(
            "Duplicate attack stage IDs detected."
        )

    provenance = chain[
        "provenance"
    ]

    if not isinstance(
        provenance,
        dict,
    ):

        raise ValueError(
            "Attack chain provenance must be an object."
        )

    if provenance.get(
        "evidence_basis"
    ) != "OBSERVED":

        raise ValueError(
            "Attack chain evidence basis "
            "must be OBSERVED."
        )

    if provenance.get(
        "network_access_performed"
    ) is not False:

        raise ValueError(
            "Attack chain construction must "
            "not perform network access."
        )
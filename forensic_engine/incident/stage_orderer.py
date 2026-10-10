"""
TRACEWEAVE - Phase 18.3
Attack Stage Ordering
"""

from typing import Any, Dict, List

from forensic_engine.incident.attack_stage import (
    STAGE_ORDER,
    validate_attack_stage,
)


def order_attack_stages(
    stages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(stages, list):
        raise ValueError(
            "Attack stages must be a list."
        )

    for stage in stages:
        validate_attack_stage(stage)

    ordered = sorted(
        stages,
        key=lambda stage: (
            STAGE_ORDER[
                stage["stage_type"]
            ],
            stage["sequence_number"],
        ),
    )

    for index, stage in enumerate(
        ordered,
        start=1,
    ):
        stage["sequence_number"] = index
        stage["stage_id"] = (
            f"STAGE-{index}-"
            f"{stage['stage_type']}"
        )

    return ordered


def validate_stage_order(
    stages: List[Dict[str, Any]],
) -> None:

    if not isinstance(stages, list):
        raise ValueError(
            "Attack stages must be a list."
        )

    previous_order = 0
    expected_sequence = 1

    for stage in stages:

        validate_attack_stage(stage)

        stage_type = stage[
            "stage_type"
        ]

        current_order = STAGE_ORDER[
            stage_type
        ]

        if current_order < previous_order:
            raise ValueError(
                "Attack stages are not in "
                "logical order."
            )

        if stage[
            "sequence_number"
        ] != expected_sequence:

            raise ValueError(
                "Attack stage sequence is not "
                "continuous."
            )

        previous_order = current_order
        expected_sequence += 1
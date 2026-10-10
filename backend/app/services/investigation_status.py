"""
TRACEWEAVE - Investigation Status Service
"""

from typing import Any, Dict, List

from backend.app.models.investigation import (
    Investigation,
)
from backend.app.services.investigation_stages import (
    INVESTIGATION_STAGES,
)


def build_stage_status(
    investigation: Investigation,
) -> List[Dict[str, Any]]:
    """
    Build the status of every investigation stage.
    """

    current_stage = (
        investigation.current_stage
    )

    if investigation.status == "PENDING":
        completed_before = -1

    elif investigation.status == "COMPLETED":
        completed_before = (
            len(INVESTIGATION_STAGES) - 1
        )

    elif investigation.status == "FAILED":
        if current_stage in INVESTIGATION_STAGES:
            completed_before = (
                INVESTIGATION_STAGES.index(
                    current_stage
                ) - 1
            )
        else:
            completed_before = -1

    else:
        if current_stage in INVESTIGATION_STAGES:
            completed_before = (
                INVESTIGATION_STAGES.index(
                    current_stage
                ) - 1
            )
        else:
            completed_before = -1

    stages = []

    for index, stage in enumerate(
        INVESTIGATION_STAGES
    ):

        if (
            investigation.status
            == "COMPLETED"
        ):
            stage_status = "COMPLETED"

        elif index <= completed_before:
            stage_status = "COMPLETED"

        elif stage == current_stage:
            if investigation.status == "FAILED":
                stage_status = "FAILED"
            else:
                stage_status = "RUNNING"

        else:
            stage_status = "PENDING"

        stages.append(
            {
                "sequence": index + 1,
                "stage": stage,
                "status": stage_status,
            }
        )

    return stages
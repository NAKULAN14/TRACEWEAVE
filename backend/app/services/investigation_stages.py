"""
TRACEWEAVE - Investigation Stage Tracking
"""

from typing import List


INVESTIGATION_STAGES: List[str] = [
    "INGESTION",
    "EMAIL_ANALYSIS",
    "ATTACHMENT_EXTRACTION",
    "ICS_ANALYSIS",
    "QR_ANALYSIS",
    "URL_ANALYSIS",
    "IOC_ANALYSIS",
    "THREAT_INTELLIGENCE",
    "INFRASTRUCTURE_CORRELATION",
    "INCIDENT_RECONSTRUCTION",
    "TIMELINE_RECONSTRUCTION",
    "ATTACK_CHAIN",
    "MITRE_MAPPING",
    "RISK_ASSESSMENT",
    "RECOMMENDATIONS",
]


def validate_stage(stage: str) -> None:
    """Validate that a stage belongs to the TRACEWEAVE pipeline."""

    if stage not in INVESTIGATION_STAGES:
        raise ValueError(
            f"Unsupported investigation stage: {stage}"
        )


def get_next_stage(
    current_stage: str,
) -> str | None:
    """
    Return the next stage in the investigation pipeline.

    Returns None when the current stage is the final stage.
    """

    validate_stage(current_stage)

    index = INVESTIGATION_STAGES.index(
        current_stage
    )

    if index == len(INVESTIGATION_STAGES) - 1:
        return None

    return INVESTIGATION_STAGES[index + 1]


def get_stage_sequence(
    stage: str,
) -> int:
    """Return the 1-based sequence number of a stage."""

    validate_stage(stage)

    return (
        INVESTIGATION_STAGES.index(stage) + 1
    )


def is_final_stage(
    stage: str,
) -> bool:
    """Check whether a stage is the final pipeline stage."""

    validate_stage(stage)

    return (
        stage == INVESTIGATION_STAGES[-1]
    )


if __name__ == "__main__":

    validate_stage("QR_ANALYSIS")

    assert (
        get_next_stage("INGESTION")
        == "EMAIL_ANALYSIS"
    )

    assert (
        get_stage_sequence("INGESTION")
        == 1
    )

    assert (
        get_stage_sequence(
            "RECOMMENDATIONS"
        )
        == len(INVESTIGATION_STAGES)
    )

    assert is_final_stage(
        "RECOMMENDATIONS"
    )

    print(
        "INVESTIGATION STAGE TRACKING: PASS"
    )

    print(
        "Total stages:",
        len(INVESTIGATION_STAGES),
    )
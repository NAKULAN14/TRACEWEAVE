"""
TRACEWEAVE - Phase 19.2
Attack Stage to MITRE ATT&CK Technique Mapping
"""

from typing import Any, Dict, List


STAGE_TECHNIQUE_CANDIDATES = {
    "DELIVERY": [
        {
            "technique_id": "T1566.001",
            "technique_name":
                "Phishing: Spearphishing Attachment",
            "tactic": "INITIAL_ACCESS",
            "condition":
                "Use only when evidence supports "
                "malicious attachment-based phishing."
        },
        {
            "technique_id": "T1566.002",
            "technique_name":
                "Phishing: Spearphishing Link",
            "tactic": "INITIAL_ACCESS",
            "condition":
                "Use only when evidence supports "
                "a phishing link delivered to the victim."
        },
    ],

    "ARTIFACT_INTERACTION": [
        {
            "technique_id": "T1204.002",
            "technique_name":
                "User Execution: Malicious File",
            "tactic": "EXECUTION",
            "condition":
                "Use only when evidence supports "
                "user execution of a malicious file."
        },
        {
            "technique_id": "T1204.001",
            "technique_name":
                "User Execution: Malicious Link",
            "tactic": "EXECUTION",
            "condition":
                "Use only when evidence supports "
                "user interaction with a malicious link."
        },
    ],

    "QR_DISCOVERY": [],

    "QR_DECODE": [],

    "URL_EXTRACTION": [],

    "IOC_EXTRACTION": [],

    "INFRASTRUCTURE_CORRELATION": [],
}


def get_candidate_techniques(
    stage_type: str,
) -> List[Dict[str, Any]]:

    if not isinstance(
        stage_type,
        str,
    ) or not stage_type.strip():

        raise ValueError(
            "stage_type must be a "
            "non-empty string."
        )

    stage_type = stage_type.upper()

    if stage_type not in (
        STAGE_TECHNIQUE_CANDIDATES
    ):
        raise ValueError(
            f"Unsupported attack stage: "
            f"{stage_type}"
        )

    return STAGE_TECHNIQUE_CANDIDATES[
        stage_type
    ]


def get_all_stage_mappings() -> Dict[
    str,
    List[Dict[str, Any]]
]:

    return {
        stage: list(techniques)
        for stage, techniques
        in STAGE_TECHNIQUE_CANDIDATES.items()
    }


def validate_stage_technique_mapping(
    mapping: Dict[str, Any],
) -> None:

    required_fields = {
        "technique_id",
        "technique_name",
        "tactic",
        "condition",
    }

    missing = (
        required_fields
        - set(mapping.keys())
    )

    if missing:
        raise ValueError(
            "Stage-technique mapping missing "
            f"fields: {sorted(missing)}"
        )

    if not mapping[
        "technique_id"
    ].strip():

        raise ValueError(
            "technique_id cannot be empty."
        )

    if not mapping[
        "technique_name"
    ].strip():

        raise ValueError(
            "technique_name cannot be empty."
        )

    if not mapping[
        "tactic"
    ].strip():

        raise ValueError(
            "tactic cannot be empty."
        )

    if not mapping[
        "condition"
    ].strip():

        raise ValueError(
            "condition cannot be empty."
        )


if __name__ == "__main__":

    for stage, mappings in (
        STAGE_TECHNIQUE_CANDIDATES.items()
    ):
        for mapping in mappings:
            validate_stage_technique_mapping(
                mapping
            )

    print(
        "STAGE → TECHNIQUE MAPPING: PASS"
    )

    for stage, mappings in (
        STAGE_TECHNIQUE_CANDIDATES.items()
    ):
        print(
            f"{stage}: "
            f"{len(mappings)} candidate(s)"
        )
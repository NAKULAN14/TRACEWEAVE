"""
TRACEWEAVE - Phase 19.1
MITRE ATT&CK Technique Model
"""

from typing import Any, Dict


SUPPORTED_TACTICS = {
    "INITIAL_ACCESS",
    "EXECUTION",
    "PERSISTENCE",
    "PRIVILEGE_ESCALATION",
    "DEFENSE_EVASION",
    "CREDENTIAL_ACCESS",
    "DISCOVERY",
    "COLLECTION",
    "COMMAND_AND_CONTROL",
    "EXFILTRATION",
    "IMPACT",
}


def create_attack_technique(
    technique_id: str,
    technique_name: str,
    tactic: str,
    description: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        technique_id,
        str,
    ) or not technique_id.strip():

        raise ValueError(
            "technique_id must be a "
            "non-empty string."
        )

    if not isinstance(
        technique_name,
        str,
    ) or not technique_name.strip():

        raise ValueError(
            "technique_name must be a "
            "non-empty string."
        )

    tactic = tactic.upper()

    if tactic not in SUPPORTED_TACTICS:
        raise ValueError(
            f"Unsupported ATT&CK tactic: {tactic}"
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
        "technique_id": technique_id.strip(),
        "technique_name":
            technique_name.strip(),
        "tactic": tactic,
        "description":
            description.strip(),
        "evidence": evidence,
        "mapping_status": "OBSERVED",
    }


def validate_attack_technique(
    technique: Dict[str, Any],
) -> None:

    required_fields = {
        "technique_id",
        "technique_name",
        "tactic",
        "description",
        "evidence",
        "mapping_status",
    }

    missing = (
        required_fields
        - set(technique.keys())
    )

    if missing:
        raise ValueError(
            "ATT&CK technique missing fields: "
            f"{sorted(missing)}"
        )

    if not technique[
        "technique_id"
    ].strip():

        raise ValueError(
            "technique_id cannot be empty."
        )

    if technique[
        "tactic"
    ] not in SUPPORTED_TACTICS:

        raise ValueError(
            "Unsupported ATT&CK tactic."
        )

    if not isinstance(
        technique["evidence"],
        dict,
    ):

        raise ValueError(
            "Technique evidence must be "
            "a dictionary."
        )

    if technique[
        "mapping_status"
    ] != "OBSERVED":

        raise ValueError(
            "Mapping status must remain OBSERVED."
        )
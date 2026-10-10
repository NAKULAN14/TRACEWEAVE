"""
TRACEWEAVE - Phase 19.3
ATT&CK Technique Evidence Linking
"""

from datetime import datetime, timezone
from typing import Any, Dict


def create_technique_evidence_link(
    technique_id: str,
    technique_name: str,
    tactic: str,
    source_event: str,
    source_artifact: str,
    source_location: str,
    explanation: str,
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

    if not isinstance(
        tactic,
        str,
    ) or not tactic.strip():

        raise ValueError(
            "tactic must be a "
            "non-empty string."
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
        "link_id": (
            f"{technique_id}:"
            f"{source_event}"
        ),
        "technique": {
            "technique_id":
                technique_id,
            "technique_name":
                technique_name,
            "tactic":
                tactic,
        },
        "evidence": {
            "source_event":
                source_event,
            "source_artifact":
                source_artifact,
            "source_location":
                source_location,
        },
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


def validate_technique_evidence_link(
    link: Dict[str, Any],
) -> None:

    required_fields = {
        "link_id",
        "technique",
        "evidence",
        "explanation",
        "mapping_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(link.keys())
    )

    if missing:
        raise ValueError(
            "Technique evidence link missing "
            f"fields: {sorted(missing)}"
        )

    technique = link[
        "technique"
    ]

    if not isinstance(
        technique,
        dict,
    ):
        raise ValueError(
            "Technique must be an object."
        )

    for field in (
        "technique_id",
        "technique_name",
        "tactic",
    ):
        if not technique.get(field):
            raise ValueError(
                f"Technique field '{field}' "
                f"cannot be empty."
            )

    evidence = link[
        "evidence"
    ]

    if not isinstance(
        evidence,
        dict,
    ):
        raise ValueError(
            "Evidence must be an object."
        )

    for field in (
        "source_event",
        "source_artifact",
        "source_location",
    ):
        if not evidence.get(field):
            raise ValueError(
                f"Evidence field '{field}' "
                f"cannot be empty."
            )

    if not link[
        "explanation"
    ]:
        raise ValueError(
            "Explanation cannot be empty."
        )

    if link[
        "mapping_status"
    ] != "OBSERVED":

        raise ValueError(
            "Mapping status must remain OBSERVED."
        )

    if link[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "Technique evidence linking must "
            "not perform network access."
        )


if __name__ == "__main__":

    link = create_technique_evidence_link(
        technique_id="T1566.001",
        technique_name=(
            "Phishing: Spearphishing Attachment"
        ),
        tactic="INITIAL_ACCESS",
        source_event="EVENT-001",
        source_artifact="email.eml",
        source_location="attachments",
        explanation=(
            "The observed attachment delivery "
            "event provides evidence supporting "
            "this ATT&CK technique mapping."
        ),
    )

    validate_technique_evidence_link(
        link
    )

    print(
        "TECHNIQUE EVIDENCE LINK: PASS"
    )
"""
TRACEWEAVE - Phase 16.1
Incident Reconstruction Evidence Link Model
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_LINK_TYPES = {
    "DERIVED_FROM",
    "CONTAINS",
    "REFERENCES",
    "ASSOCIATED_WITH",
}


def create_evidence_link(
    link_type: str,
    source_artifact: str,
    target_artifact: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    link_type = link_type.upper()

    if link_type not in SUPPORTED_LINK_TYPES:
        raise ValueError(
            f"Unsupported evidence link type: "
            f"{link_type}"
        )

    if not isinstance(
        source_artifact,
        str,
    ) or not source_artifact.strip():

        raise ValueError(
            "Source artifact must be a "
            "non-empty string."
        )

    if not isinstance(
        target_artifact,
        str,
    ) or not target_artifact.strip():

        raise ValueError(
            "Target artifact must be a "
            "non-empty string."
        )

    if not isinstance(
        evidence,
        dict,
    ):
        raise ValueError(
            "Evidence must be a dictionary."
        )

    source_artifact = (
        source_artifact.strip()
    )

    target_artifact = (
        target_artifact.strip()
    )

    link_id = (
        f"{source_artifact}"
        f"->{link_type}->"
        f"{target_artifact}"
    )

    return {
        "link_id": link_id,
        "link_type": link_type,
        "source": {
            "artifact": source_artifact,
        },
        "target": {
            "artifact": target_artifact,
        },
        "evidence": evidence,
        "observed_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def validate_evidence_link(
    link: Dict[str, Any],
) -> None:

    required_fields = {
        "link_id",
        "link_type",
        "source",
        "target",
        "evidence",
        "observed_at",
    }

    missing = (
        required_fields
        - set(link.keys())
    )

    if missing:
        raise ValueError(
            "Evidence link missing fields: "
            f"{sorted(missing)}"
        )

    if link["link_type"] not in (
        SUPPORTED_LINK_TYPES
    ):
        raise ValueError(
            f"Unsupported evidence link type: "
            f"{link['link_type']}"
        )

    source = link["source"]
    target = link["target"]

    if not isinstance(
        source,
        dict,
    ):
        raise ValueError(
            "Evidence link source must "
            "be an object."
        )

    if not isinstance(
        target,
        dict,
    ):
        raise ValueError(
            "Evidence link target must "
            "be an object."
        )

    source_artifact = source.get(
        "artifact"
    )

    target_artifact = target.get(
        "artifact"
    )

    if not source_artifact:
        raise ValueError(
            "Source artifact is missing."
        )

    if not target_artifact:
        raise ValueError(
            "Target artifact is missing."
        )

    expected_id = (
        f"{source_artifact}"
        f"->{link['link_type']}->"
        f"{target_artifact}"
    )

    if link["link_id"] != expected_id:
        raise ValueError(
            "Evidence link ID does not match "
            "source/type/target."
        )

    if not isinstance(
        link["evidence"],
        dict,
    ):
        raise ValueError(
            "Evidence must be an object."
        )
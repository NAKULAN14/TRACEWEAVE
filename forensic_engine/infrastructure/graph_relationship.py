"""
TRACEWEAVE - Phase 15.2
Infrastructure Graph Relationship Model
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_RELATIONSHIP_TYPES = {
    "RESOLVES_TO",
    "PRESENTS_CERTIFICATE",
}


def create_graph_relationship(
    relationship_type: str,
    source_node_id: str,
    target_node_id: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    relationship_type = relationship_type.upper()

    if relationship_type not in SUPPORTED_RELATIONSHIP_TYPES:
        raise ValueError(
            f"Unsupported relationship type: "
            f"{relationship_type}"
        )

    if not source_node_id.strip():
        raise ValueError(
            "Source node ID cannot be empty."
        )

    if not target_node_id.strip():
        raise ValueError(
            "Target node ID cannot be empty."
        )

    if not isinstance(evidence, dict):
        raise ValueError(
            "Evidence must be a dictionary."
        )

    return {
        "relationship_id": (
            f"{source_node_id}"
            f"->{relationship_type}->"
            f"{target_node_id}"
        ),
        "relationship_type": relationship_type,
        "source": {
            "node_id": source_node_id,
        },
        "target": {
            "node_id": target_node_id,
        },
        "evidence": evidence,
        "observed_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def validate_graph_relationship(
    relationship: Dict[str, Any],
) -> None:

    required_fields = {
        "relationship_id",
        "relationship_type",
        "source",
        "target",
        "evidence",
        "observed_at",
    }

    missing = required_fields - set(
        relationship.keys()
    )

    if missing:
        raise ValueError(
            "Graph relationship missing fields: "
            f"{sorted(missing)}"
        )

    relationship_type = relationship[
        "relationship_type"
    ]

    if relationship_type not in (
        SUPPORTED_RELATIONSHIP_TYPES
    ):
        raise ValueError(
            f"Unsupported relationship type: "
            f"{relationship_type}"
        )

    source = relationship["source"]
    target = relationship["target"]

    if not isinstance(source, dict):
        raise ValueError(
            "Relationship source must be an object."
        )

    if not isinstance(target, dict):
        raise ValueError(
            "Relationship target must be an object."
        )

    source_id = source.get("node_id")
    target_id = target.get("node_id")

    if not source_id:
        raise ValueError(
            "Relationship source node_id is missing."
        )

    if not target_id:
        raise ValueError(
            "Relationship target node_id is missing."
        )

    expected_id = (
        f"{source_id}"
        f"->{relationship_type}->"
        f"{target_id}"
    )

    if relationship["relationship_id"] != expected_id:
        raise ValueError(
            "Relationship ID does not match "
            "source/type/target."
        )

    if not isinstance(
        relationship["evidence"],
        dict,
    ):
        raise ValueError(
            "Relationship evidence must be an object."
        )
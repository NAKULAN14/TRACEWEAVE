"""
TRACEWEAVE - Phase 15.1
Infrastructure Graph Node Model
"""

from datetime import datetime, timezone
from typing import Any, Dict


SUPPORTED_NODE_TYPES = {
    "DOMAIN",
    "IP",
    "TLS_CERTIFICATE",
}


def create_graph_node(
    node_type: str,
    value: str,
    source: str = "TRACEWEAVE",
) -> Dict[str, Any]:

    node_type = node_type.upper()

    if node_type not in SUPPORTED_NODE_TYPES:
        raise ValueError(
            f"Unsupported graph node type: {node_type}"
        )

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "Graph node value must be a non-empty string."
        )

    return {
        "node_id": f"{node_type}:{value.strip()}",
        "node_type": node_type,
        "value": value.strip(),
        "source": source,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def validate_graph_node(
    node: Dict[str, Any],
) -> None:

    required_fields = {
        "node_id",
        "node_type",
        "value",
        "source",
        "created_at",
    }

    missing = required_fields - set(
        node.keys()
    )

    if missing:
        raise ValueError(
            f"Graph node missing fields: {sorted(missing)}"
        )

    if node["node_type"] not in SUPPORTED_NODE_TYPES:
        raise ValueError(
            f"Unsupported node type: {node['node_type']}"
        )

    expected_id = (
        f"{node['node_type']}:{node['value']}"
    )

    if node["node_id"] != expected_id:
        raise ValueError(
            "Graph node ID does not match node type/value."
        )
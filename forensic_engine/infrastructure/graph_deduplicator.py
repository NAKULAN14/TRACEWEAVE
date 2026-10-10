"""
TRACEWEAVE - Phase 15.3
Infrastructure Graph Node Deduplication
"""

from typing import Any, Dict, Iterable, List, Tuple

from forensic_engine.infrastructure.graph_node import (
    create_graph_node,
    validate_graph_node,
)


def node_identity(
    node_type: str,
    value: str,
) -> Tuple[str, str]:

    return (
        node_type.upper(),
        value.strip(),
    )


def deduplicate_nodes(
    nodes: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    unique_nodes: Dict[
        Tuple[str, str],
        Dict[str, Any],
    ] = {}

    for node in nodes:

        if not isinstance(node, dict):
            raise ValueError(
                "Every node must be a dictionary."
            )

        node_type = node.get(
            "node_type"
        )

        value = node.get(
            "value"
        )

        if not node_type or not value:
            raise ValueError(
                "Node must contain node_type and value."
            )

        # Validate the supplied node first.
        validate_graph_node(node)

        identity = node_identity(
            node_type,
            value,
        )

        if identity not in unique_nodes:
            unique_nodes[identity] = node

    return list(
        unique_nodes.values()
    )


def build_nodes_from_relationships(
    relationships: Iterable[
        Dict[str, Any]
    ],
) -> List[Dict[str, Any]]:

    nodes: List[Dict[str, Any]] = []

    for relationship in relationships:

        source = relationship.get(
            "source",
            {}
        )

        target = relationship.get(
            "target",
            {}
        )

        source_id = source.get(
            "node_id",
            ""
        )

        target_id = target.get(
            "node_id",
            ""
        )

        for node_id in (
            source_id,
            target_id,
        ):

            if not node_id:
                continue

            if ":" not in node_id:
                raise ValueError(
                    f"Invalid node ID: {node_id}"
                )

            node_type, value = (
                node_id.split(
                    ":",
                    1,
                )
            )

            nodes.append(
                create_graph_node(
                    node_type,
                    value,
                )
            )

    return deduplicate_nodes(
        nodes
    )


def deduplication_summary(
    original_nodes: int,
    unique_nodes: int,
) -> Dict[str, Any]:

    return {
        "original_node_count":
            original_nodes,
        "unique_node_count":
            unique_nodes,
        "duplicate_node_count":
            original_nodes - unique_nodes,
    }
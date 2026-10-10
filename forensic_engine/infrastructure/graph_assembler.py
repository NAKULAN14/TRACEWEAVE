"""
TRACEWEAVE - Phase 15.5
Infrastructure Graph Assembly
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.infrastructure.graph_node import (
    validate_graph_node,
)

from forensic_engine.infrastructure.graph_relationship import (
    validate_graph_relationship,
)


def assemble_graph(
    nodes: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
) -> Dict[str, Any]:

    if not isinstance(nodes, list):
        raise ValueError(
            "Graph nodes must be a list."
        )

    if not isinstance(relationships, list):
        raise ValueError(
            "Graph relationships must be a list."
        )

    # Validate every node.
    for node in nodes:
        validate_graph_node(node)

    # Validate every relationship.
    for relationship in relationships:
        validate_graph_relationship(
            relationship
        )

    node_ids = {
        node["node_id"]
        for node in nodes
    }

    # Every relationship must point to an
    # existing graph node.
    for relationship in relationships:

        source_id = relationship[
            "source"
        ]["node_id"]

        target_id = relationship[
            "target"
        ]["node_id"]

        if source_id not in node_ids:
            raise ValueError(
                f"Relationship references missing "
                f"source node: {source_id}"
            )

        if target_id not in node_ids:
            raise ValueError(
                f"Relationship references missing "
                f"target node: {target_id}"
            )

    return {
        "graph_type": "TRACEWEAVE_INFRASTRUCTURE",
        "schema_version": "1.0",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "network_access_performed": False,
        "summary": {
            "node_count": len(nodes),
            "relationship_count": len(
                relationships
            ),
            "node_type_counts": _count_node_types(
                nodes
            ),
            "relationship_type_counts":
                _count_relationship_types(
                    relationships
                ),
        },
        "nodes": nodes,
        "relationships": relationships,
    }


def _count_node_types(
    nodes: List[Dict[str, Any]],
) -> Dict[str, int]:

    counts: Dict[str, int] = {}

    for node in nodes:

        node_type = node[
            "node_type"
        ]

        counts[node_type] = (
            counts.get(
                node_type,
                0,
            ) + 1
        )

    return counts


def _count_relationship_types(
    relationships: List[Dict[str, Any]],
) -> Dict[str, int]:

    counts: Dict[str, int] = {}

    for relationship in relationships:

        relationship_type = relationship[
            "relationship_type"
        ]

        counts[relationship_type] = (
            counts.get(
                relationship_type,
                0,
            ) + 1
        )

    return counts


def validate_graph(
    graph: Dict[str, Any],
) -> None:

    required_fields = {
        "graph_type",
        "schema_version",
        "created_at",
        "network_access_performed",
        "summary",
        "nodes",
        "relationships",
    }

    missing = required_fields - set(
        graph.keys()
    )

    if missing:
        raise ValueError(
            "Graph missing fields: "
            f"{sorted(missing)}"
        )

    if graph[
        "graph_type"
    ] != "TRACEWEAVE_INFRASTRUCTURE":

        raise ValueError(
            "Invalid graph type."
        )

    if graph[
        "network_access_performed"
    ] is not False:

        raise ValueError(
            "Infrastructure graph must "
            "record network access as false."
        )

    nodes = graph["nodes"]
    relationships = graph[
        "relationships"
    ]

    if not isinstance(nodes, list):
        raise ValueError(
            "Graph nodes must be a list."
        )

    if not isinstance(
        relationships,
        list,
    ):
        raise ValueError(
            "Graph relationships must be a list."
        )

    # Validate node uniqueness.
    node_ids = [
        node["node_id"]
        for node in nodes
    ]

    if len(node_ids) != len(
        set(node_ids)
    ):
        raise ValueError(
            "Graph contains duplicate node IDs."
        )

    # Validate relationship uniqueness.
    relationship_ids = [
        relationship[
            "relationship_id"
        ]
        for relationship in relationships
    ]

    if len(relationship_ids) != len(
        set(relationship_ids)
    ):
        raise ValueError(
            "Graph contains duplicate relationship IDs."
        )

    # Ensure relationships reference
    # existing nodes.
    node_id_set = set(node_ids)

    for relationship in relationships:

        source_id = relationship[
            "source"
        ]["node_id"]

        target_id = relationship[
            "target"
        ]["node_id"]

        if source_id not in node_id_set:
            raise ValueError(
                f"Missing source node: {source_id}"
            )

        if target_id not in node_id_set:
            raise ValueError(
                f"Missing target node: {target_id}"
            )
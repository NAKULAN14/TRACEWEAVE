"""
TRACEWEAVE - Phase 15.4
Infrastructure Graph Relationship Construction
"""

from typing import Any, Dict, List

from forensic_engine.infrastructure.graph_relationship import (
    create_graph_relationship,
    validate_graph_relationship,
)


def build_graph_relationship(
    relationship: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(relationship, dict):
        raise ValueError(
            "Infrastructure relationship must be a dictionary."
        )

    relationship_type = relationship.get(
        "relationship_type"
    )

    source = relationship.get(
        "source",
        {}
    )

    target = relationship.get(
        "target",
        {}
    )

    source_type = source.get("type")
    source_value = source.get("value")

    target_type = target.get("type")
    target_value = target.get("value")

    if not source_type or not source_value:
        raise ValueError(
            "Infrastructure relationship has an invalid source."
        )

    if not target_type or not target_value:
        raise ValueError(
            "Infrastructure relationship has an invalid target."
        )

    source_node_id = (
        f"{source_type.upper()}:{source_value}"
    )

    target_node_id = (
        f"{target_type.upper()}:{target_value}"
    )

    evidence = dict(
        relationship.get(
            "evidence",
            {}
        )
    )

    # Preserve infrastructure-level provenance
    # when it exists.
    if "provenance" in relationship:
        evidence["provenance"] = relationship[
            "provenance"
        ]

    if "observed_at" in relationship:
        evidence["observed_at"] = relationship[
            "observed_at"
        ]

    if "network_access_performed" in relationship:
        evidence[
            "network_access_performed"
        ] = relationship[
            "network_access_performed"
        ]

    graph_relationship = create_graph_relationship(
        relationship_type=relationship_type,
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        evidence=evidence,
    )

    validate_graph_relationship(
        graph_relationship
    )

    return graph_relationship


def build_graph_relationships(
    relationships: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(
        relationships,
        list,
    ):
        raise ValueError(
            "Relationships must be provided as a list."
        )

    results = []

    seen = set()

    for relationship in relationships:

        graph_relationship = (
            build_graph_relationship(
                relationship
            )
        )

        relationship_id = (
            graph_relationship[
                "relationship_id"
            ]
        )

        if relationship_id in seen:
            continue

        seen.add(
            relationship_id
        )

        results.append(
            graph_relationship
        )

    return results
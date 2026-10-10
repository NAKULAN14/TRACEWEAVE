"""
TRACEWEAVE - Phase 15.7
Infrastructure Graph Validation
"""

import json
import os
import sys
from typing import Any, Dict, List, Set

from forensic_engine.infrastructure.graph_assembler import (
    validate_graph,
)


GRAPH_PATH = os.path.join(
    "reports",
    "phase15",
    "infrastructure_graph.json",
)


def load_graph(path: str) -> Dict[str, Any]:
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def validate_graph_contents(
    graph: Dict[str, Any],
) -> List[str]:

    errors: List[str] = []

    try:
        validate_graph(graph)
    except Exception as exc:
        errors.append(
            f"Graph schema validation failed: {exc}"
        )
        return errors

    nodes = graph["nodes"]
    relationships = graph[
        "relationships"
    ]

    node_ids: Set[str] = {
        node["node_id"]
        for node in nodes
    }

    # --------------------------------------------------
    # Node validation
    # --------------------------------------------------

    for index, node in enumerate(nodes):

        if not node.get("node_id"):
            errors.append(
                f"Node[{index}] has no node_id."
            )

        if not node.get("node_type"):
            errors.append(
                f"Node[{index}] has no node_type."
            )

        if not node.get("value"):
            errors.append(
                f"Node[{index}] has no value."
            )

        expected_id = (
            f"{node.get('node_type')}:"
            f"{node.get('value')}"
        )

        if node.get("node_id") != expected_id:
            errors.append(
                f"Node[{index}] has inconsistent node_id."
            )

    # --------------------------------------------------
    # Relationship validation
    # --------------------------------------------------

    relationship_ids: Set[str] = set()

    for index, relationship in enumerate(
        relationships
    ):

        relationship_id = relationship.get(
            "relationship_id"
        )

        if not relationship_id:
            errors.append(
                f"Relationship[{index}] has no ID."
            )
            continue

        if relationship_id in relationship_ids:
            errors.append(
                f"Duplicate relationship: "
                f"{relationship_id}"
            )

        relationship_ids.add(
            relationship_id
        )

        source_id = relationship[
            "source"
        ].get("node_id")

        target_id = relationship[
            "target"
        ].get("node_id")

        if source_id not in node_ids:
            errors.append(
                f"Relationship[{index}] references "
                f"missing source node: {source_id}"
            )

        if target_id not in node_ids:
            errors.append(
                f"Relationship[{index}] references "
                f"missing target node: {target_id}"
            )

        if not relationship.get(
            "evidence"
        ):
            errors.append(
                f"Relationship[{index}] has no evidence."
            )

    # --------------------------------------------------
    # Summary validation
    # --------------------------------------------------

    summary = graph.get(
        "summary",
        {}
    )

    if summary.get(
        "node_count"
    ) != len(nodes):

        errors.append(
            "Summary node_count does not "
            "match actual node count."
        )

    if summary.get(
        "relationship_count"
    ) != len(relationships):

        errors.append(
            "Summary relationship_count does not "
            "match actual relationship count."
        )

    # --------------------------------------------------
    # Network access validation
    # --------------------------------------------------

    if graph.get(
        "network_access_performed"
    ) is not False:

        errors.append(
            "Graph must record "
            "network_access_performed=false."
        )

    return errors


def main() -> None:

    if not os.path.exists(
        GRAPH_PATH
    ):

        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "errors": [
                        "Infrastructure graph does not exist."
                    ],
                },
                indent=2,
            )
        )

        sys.exit(1)

    try:

        graph = load_graph(
            GRAPH_PATH
        )

    except Exception as exc:

        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "errors": [
                        f"Unable to load graph: {exc}"
                    ],
                },
                indent=2,
            )
        )

        sys.exit(1)

    errors = validate_graph_contents(
        graph
    )

    result = {
        "status": (
            "PASS"
            if not errors
            else "FAIL"
        ),
        "graph_path": GRAPH_PATH,
        "node_count": len(
            graph.get(
                "nodes",
                []
            )
        ),
        "relationship_count": len(
            graph.get(
                "relationships",
                []
            )
        ),
        "errors": errors,
        "network_access_performed":
            graph.get(
                "network_access_performed"
            ),
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
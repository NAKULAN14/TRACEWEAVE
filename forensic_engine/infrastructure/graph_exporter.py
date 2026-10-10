"""
TRACEWEAVE - Phase 15.6
Infrastructure Graph Export
"""

import json
import os
from typing import Any, Dict

from forensic_engine.infrastructure.graph_assembler import (
    validate_graph,
)


DEFAULT_OUTPUT = os.path.join(
    "reports",
    "phase15",
    "infrastructure_graph.json",
)


def export_graph(
    graph: Dict[str, Any],
    output_path: str = DEFAULT_OUTPUT,
) -> str:

    # Validate before writing anything.
    validate_graph(graph)

    output_dir = os.path.dirname(
        output_path
    )

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True,
        )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            graph,
            file,
            indent=2,
        )

    return output_path


def load_graph(
    input_path: str,
) -> Dict[str, Any]:

    if not os.path.exists(
        input_path
    ):
        raise FileNotFoundError(
            f"Graph file not found: {input_path}"
        )

    with open(
        input_path,
        "r",
        encoding="utf-8",
    ) as file:

        graph = json.load(file)

    validate_graph(graph)

    return graph
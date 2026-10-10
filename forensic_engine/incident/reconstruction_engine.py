"""
TRACEWEAVE - Phase 16.4
Incident Reconstruction Engine

Combines previously generated forensic evidence into
an incident object without making maliciousness claims.
"""

from typing import Any, Dict, List

from forensic_engine.incident.incident_object import (
    add_artifact,
    add_evidence_link,
    add_ioc,
    attach_infrastructure_graph,
    set_status,
    validate_incident,
)


def reconstruct_incident(
    incident: Dict[str, Any],
    artifacts: List[Dict[str, Any]],
    evidence_links: List[Dict[str, Any]],
    iocs: List[Dict[str, Any]],
    infrastructure_graph: Dict[str, Any] = None,
) -> Dict[str, Any]:

    if not isinstance(
        incident,
        dict,
    ):
        raise ValueError(
            "Incident must be a dictionary."
        )

    if not isinstance(
        artifacts,
        list,
    ):
        raise ValueError(
            "Artifacts must be a list."
        )

    if not isinstance(
        evidence_links,
        list,
    ):
        raise ValueError(
            "Evidence links must be a list."
        )

    if not isinstance(
        iocs,
        list,
    ):
        raise ValueError(
            "IOCs must be a list."
        )

    # -----------------------------------------------
    # Add artifacts
    # -----------------------------------------------

    for artifact in artifacts:
        add_artifact(
            incident,
            artifact,
        )

    # -----------------------------------------------
    # Add evidence relationships
    # -----------------------------------------------

    for link in evidence_links:
        add_evidence_link(
            incident,
            link,
        )

    # -----------------------------------------------
    # Add canonical IOCs
    # -----------------------------------------------

    for ioc in iocs:
        add_ioc(
            incident,
            ioc,
        )

    # -----------------------------------------------
    # Attach infrastructure graph
    # -----------------------------------------------

    if infrastructure_graph is not None:
        attach_infrastructure_graph(
            incident,
            infrastructure_graph,
        )

    # -----------------------------------------------
    # Reconstruction status
    # -----------------------------------------------

    set_status(
        incident,
        "RECONSTRUCTED",
    )

    validate_incident(
        incident
    )

    return incident


def summarize_reconstruction(
    incident: Dict[str, Any],
) -> Dict[str, Any]:

    validate_incident(
        incident
    )

    graph = incident.get(
        "infrastructure_graph"
    )

    graph_summary = None

    if isinstance(
        graph,
        dict,
    ):
        graph_summary = graph.get(
            "summary"
        )

    return {
        "incident_id": incident[
            "incident_id"
        ],
        "case_id": incident[
            "case_id"
        ],
        "status": incident[
            "status"
        ],
        "artifact_count": len(
            incident[
                "artifacts"
            ]
        ),
        "evidence_link_count": len(
            incident[
                "evidence_links"
            ]
        ),
        "ioc_count": len(
            incident[
                "iocs"
            ]
        ),
        "infrastructure_graph": (
            graph_summary
        ),
        "reconstruction_basis": {
            "artifacts": "OBSERVED",
            "evidence_links": "OBSERVED",
            "iocs": "OBSERVED",
            "infrastructure_relationships":
                "OBSERVED",
        },
    }
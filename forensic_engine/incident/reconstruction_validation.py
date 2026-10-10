"""
TRACEWEAVE - Phase 16.6
Incident Reconstruction Validation
"""

import json
import os
import sys
from typing import Any, Dict, List, Set

from forensic_engine.incident.incident_object import (
    validate_incident,
)

from forensic_engine.incident.evidence_link import (
    validate_evidence_link,
)

from forensic_engine.incident.reconstruction_provenance import (
    validate_reconstruction_provenance,
)


def validate_reconstruction(
    incident: Dict[str, Any],
) -> List[str]:

    errors: List[str] = []

    # -----------------------------------------------
    # Incident schema
    # -----------------------------------------------

    try:
        validate_incident(incident)
    except Exception as exc:
        errors.append(
            f"Incident validation failed: {exc}"
        )
        return errors

    # -----------------------------------------------
    # Artifact uniqueness
    # -----------------------------------------------

    artifact_ids: List[str] = [
        artifact.get("artifact_id")
        for artifact in incident[
            "artifacts"
        ]
    ]

    if len(artifact_ids) != len(
        set(artifact_ids)
    ):
        errors.append(
            "Duplicate artifact IDs detected."
        )

    # -----------------------------------------------
    # Evidence links
    # -----------------------------------------------

    link_ids: Set[str] = set()

    for index, link in enumerate(
        incident["evidence_links"]
    ):

        try:
            validate_evidence_link(link)
        except Exception as exc:
            errors.append(
                f"Evidence link [{index}] invalid: {exc}"
            )

        link_id = link.get(
            "link_id"
        )

        if link_id in link_ids:
            errors.append(
                f"Duplicate evidence link: {link_id}"
            )

        link_ids.add(link_id)

    # -----------------------------------------------
    # Evidence links must reference
    # existing artifacts
    # -----------------------------------------------

    artifact_set = set(
        artifact_ids
    )

    for index, link in enumerate(
        incident["evidence_links"]
    ):

        source = link.get(
            "source",
            {}
        )

        target = link.get(
            "target",
            {}
        )

        source_artifact = source.get(
            "artifact"
        )

        target_artifact = target.get(
            "artifact"
        )

        if source_artifact not in artifact_set:
            errors.append(
                f"Evidence link [{index}] references "
                f"missing source artifact: "
                f"{source_artifact}"
            )

        if target_artifact not in artifact_set:
            errors.append(
                f"Evidence link [{index}] references "
                f"missing target artifact: "
                f"{target_artifact}"
            )

    # -----------------------------------------------
    # IOC validation
    # -----------------------------------------------

    ioc_keys = set()

    for index, ioc in enumerate(
        incident["iocs"]
    ):

        ioc_type = ioc.get(
            "ioc_type"
        )

        value = ioc.get(
            "canonical_value"
        )

        if not ioc_type:
            errors.append(
                f"IOC [{index}] missing ioc_type."
            )

        if not value:
            errors.append(
                f"IOC [{index}] missing canonical_value."
            )

        key = (
            ioc_type,
            value,
        )

        if key in ioc_keys:
            errors.append(
                f"Duplicate IOC: {key}"
            )

        ioc_keys.add(key)

    # -----------------------------------------------
    # Infrastructure graph
    # -----------------------------------------------

    graph = incident.get(
        "infrastructure_graph"
    )

    if graph is not None:

        if not isinstance(
            graph,
            dict,
        ):
            errors.append(
                "Infrastructure graph must be an object."
            )

        else:

            if graph.get(
                "network_access_performed"
            ) is not False:

                errors.append(
                    "Infrastructure graph has "
                    "network access enabled."
                )

            node_ids = {
                node.get("node_id")
                for node in graph.get(
                    "nodes",
                    []
                )
            }

            for index, relationship in enumerate(
                graph.get(
                    "relationships",
                    []
                )
            ):

                source_id = (
                    relationship.get(
                        "source",
                        {}
                    ).get("node_id")
                )

                target_id = (
                    relationship.get(
                        "target",
                        {}
                    ).get("node_id")
                )

                if source_id not in node_ids:
                    errors.append(
                        f"Graph relationship [{index}] "
                        f"references missing source node."
                    )

                if target_id not in node_ids:
                    errors.append(
                        f"Graph relationship [{index}] "
                        f"references missing target node."
                    )

    # -----------------------------------------------
    # Timeline and attack stages
    # -----------------------------------------------

    if not isinstance(
        incident["timeline_events"],
        list,
    ):
        errors.append(
            "timeline_events must be a list."
        )

    if not isinstance(
        incident["attack_stages"],
        list,
    ):
        errors.append(
            "attack_stages must be a list."
        )

    # -----------------------------------------------
    # Findings
    # -----------------------------------------------

    if not isinstance(
        incident["findings"],
        list,
    ):
        errors.append(
            "findings must be a list."
        )

    return errors


def main() -> None:

    # Phase 16 currently validates the incident
    # object itself. The reconstruction engine will
    # persist complete incidents in later steps.
    #
    # For now, run a controlled validation fixture.

    test_incident = {
        "incident_id": "INC-TRACEWEAVE-VALIDATION",
        "case_id": "TRACEWEAVE-VALIDATION",
        "title": "TRACEWEAVE Reconstruction Validation",
        "status": "RECONSTRUCTED",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "artifacts": [
            {
                "artifact_id": "email.eml"
            },
            {
                "artifact_id": "event.ics"
            },
        ],
        "evidence_links": [],
        "iocs": [],
        "infrastructure_graph": None,
        "timeline_events": [],
        "attack_stages": [],
        "findings": [],
    }

    errors = validate_reconstruction(
        test_incident
    )

    result = {
        "status": (
            "PASS"
            if not errors
            else "FAIL"
        ),
        "artifact_count": len(
            test_incident[
                "artifacts"
            ]
        ),
        "evidence_link_count": len(
            test_incident[
                "evidence_links"
            ]
        ),
        "ioc_count": len(
            test_incident[
                "iocs"
            ]
        ),
        "errors": errors,
        "validation_scope": [
            "incident_schema",
            "artifact_uniqueness",
            "evidence_links",
            "artifact_references",
            "ioc_structure",
            "ioc_uniqueness",
            "infrastructure_graph",
            "timeline_structure",
            "attack_stage_structure",
            "finding_structure",
        ],
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
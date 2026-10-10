"""
TRACEWEAVE - Phase 16.2
Cross-Layer Artifact Relationships
"""

from typing import Any, Dict, List

from forensic_engine.incident.evidence_link import (
    create_evidence_link,
    validate_evidence_link,
)


CROSS_LAYER_LINK_TYPES = {
    "CONTAINS",
    "EXTRACTED_FROM",
    "DECODED_FROM",
    "REFERENCES",
    "DERIVED_FROM",
}


def create_cross_layer_link(
    link_type: str,
    source_artifact: str,
    target_artifact: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    link_type = link_type.upper()

    if link_type not in CROSS_LAYER_LINK_TYPES:
        raise ValueError(
            f"Unsupported cross-layer link type: "
            f"{link_type}"
        )

    link = create_evidence_link(
        link_type=link_type,
        source_artifact=source_artifact,
        target_artifact=target_artifact,
        evidence=evidence,
    )

    validate_evidence_link(link)

    return link


def build_cross_layer_links(
    links: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not isinstance(links, list):
        raise ValueError(
            "Cross-layer links must be a list."
        )

    results = []
    seen = set()

    for link in links:

        if not isinstance(link, dict):
            raise ValueError(
                "Every cross-layer link must "
                "be a dictionary."
            )

        built_link = create_cross_layer_link(
            link_type=link[
                "link_type"
            ],
            source_artifact=link[
                "source_artifact"
            ],
            target_artifact=link[
                "target_artifact"
            ],
            evidence=link.get(
                "evidence",
                {},
            ),
        )

        link_id = built_link[
            "link_id"
        ]

        if link_id in seen:
            continue

        seen.add(link_id)
        results.append(
            built_link
        )

    return results
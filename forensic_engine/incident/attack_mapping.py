"""
TRACEWEAVE - Phase 19.4
MITRE ATT&CK Mapping Construction
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.incident.technique_evidence_link import (
    validate_technique_evidence_link,
)


def build_attack_mapping(
    case_id: str,
    technique_links: List[Dict[str, Any]],
) -> Dict[str, Any]:

    if not isinstance(
        case_id,
        str,
    ) or not case_id.strip():

        raise ValueError(
            "case_id must be a non-empty string."
        )

    if not isinstance(
        technique_links,
        list,
    ):

        raise ValueError(
            "technique_links must be a list."
        )

    for link in technique_links:
        validate_technique_evidence_link(
            link
        )

    # Deduplicate technique mappings by
    # technique + source event.
    unique_links = {}

    for link in technique_links:

        technique_id = link[
            "technique"
        ]["technique_id"]

        source_event = link[
            "evidence"
        ]["source_event"]

        identity = (
            technique_id,
            source_event,
        )

        unique_links[
            identity
        ] = link

    links = list(
        unique_links.values()
    )

    techniques = {}

    for link in links:

        technique = link[
            "technique"
        ]

        technique_id = technique[
            "technique_id"
        ]

        if technique_id not in techniques:

            techniques[
                technique_id
            ] = {
                "technique_id":
                    technique_id,
                "technique_name":
                    technique["technique_name"],
                "tactic":
                    technique["tactic"],
                "evidence_links": [],
                "mapping_status":
                    "OBSERVED",
            }

        techniques[
            technique_id
        ]["evidence_links"].append(
            link
        )

    mapping = {
        "attack_mapping_id":
            f"ATTACK-MAP-{case_id}",
        "case_id":
            case_id,
        "mapping_type":
            "TRACEWEAVE_MITRE_ATTACK_MAPPING",
        "schema_version":
            "1.0",
        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "mapping_status":
            "OBSERVED",
        "technique_count":
            len(techniques),
        "evidence_link_count":
            len(links),
        "techniques":
            list(
                techniques.values()
            ),
        "provenance": {
            "construction_method":
                "EVIDENCE_LINK_AGGREGATION",
            "evidence_basis":
                "OBSERVED",
            "network_access_performed":
                False,
        },
    }

    validate_attack_mapping(
        mapping
    )

    return mapping


def validate_attack_mapping(
    mapping: Dict[str, Any],
) -> None:

    required_fields = {
        "attack_mapping_id",
        "case_id",
        "mapping_type",
        "schema_version",
        "created_at",
        "mapping_status",
        "technique_count",
        "evidence_link_count",
        "techniques",
        "provenance",
    }

    missing = (
        required_fields
        - set(mapping.keys())
    )

    if missing:
        raise ValueError(
            "ATT&CK mapping missing fields: "
            f"{sorted(missing)}"
        )

    if mapping[
        "mapping_type"
    ] != "TRACEWEAVE_MITRE_ATTACK_MAPPING":

        raise ValueError(
            "Invalid ATT&CK mapping type."
        )

    if mapping[
        "schema_version"
    ] != "1.0":

        raise ValueError(
            "Unsupported ATT&CK mapping schema."
        )

    if mapping[
        "mapping_status"
    ] != "OBSERVED":

        raise ValueError(
            "Mapping status must remain OBSERVED."
        )

    techniques = mapping[
        "techniques"
    ]

    if not isinstance(
        techniques,
        list,
    ):

        raise ValueError(
            "techniques must be a list."
        )

    if mapping[
        "technique_count"
    ] != len(techniques):

        raise ValueError(
            "Technique count does not match "
            "actual technique count."
        )

    technique_ids = set()
    total_links = 0

    for technique in techniques:

        required = {
            "technique_id",
            "technique_name",
            "tactic",
            "evidence_links",
            "mapping_status",
        }

        missing_technique = (
            required
            - set(technique.keys())
        )

        if missing_technique:
            raise ValueError(
                "Technique mapping missing "
                f"fields: {sorted(missing_technique)}"
            )

        technique_id = technique[
            "technique_id"
        ]

        if technique_id in technique_ids:
            raise ValueError(
                f"Duplicate technique: "
                f"{technique_id}"
            )

        technique_ids.add(
            technique_id
        )

        if technique[
            "mapping_status"
        ] != "OBSERVED":

            raise ValueError(
                f"Technique {technique_id} "
                f"is not OBSERVED."
            )

        evidence_links = technique[
            "evidence_links"
        ]

        if not evidence_links:
            raise ValueError(
                f"Technique {technique_id} "
                f"has no evidence links."
            )

        for link in evidence_links:

            validate_technique_evidence_link(
                link
            )

        total_links += len(
            evidence_links
        )

    if mapping[
        "evidence_link_count"
    ] != total_links:

        raise ValueError(
            "Evidence-link count does not "
            "match actual count."
        )

    provenance = mapping[
        "provenance"
    ]

    if provenance.get(
        "evidence_basis"
    ) != "OBSERVED":

        raise ValueError(
            "ATT&CK mapping evidence basis "
            "must be OBSERVED."
        )

    if provenance.get(
        "network_access_performed"
    ) is not False:

        raise ValueError(
            "ATT&CK mapping construction must "
            "not perform network access."
        )


if __name__ == "__main__":

    from forensic_engine.incident.technique_evidence_link import (
        create_technique_evidence_link,
    )

    link = create_technique_evidence_link(
        technique_id="T1566.001",
        technique_name=(
            "Phishing: Spearphishing Attachment"
        ),
        tactic="INITIAL_ACCESS",
        source_event="EVENT-001",
        source_artifact="email.eml",
        source_location="attachments",
        explanation=(
            "Observed attachment delivery "
            "supports this mapping."
        ),
    )

    mapping = build_attack_mapping(
        "TW-TEST-001",
        [link],
    )

    validate_attack_mapping(
        mapping
    )

    print(
        "ATT&CK MAPPING CONSTRUCTION: PASS"
    )
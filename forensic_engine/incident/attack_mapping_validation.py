"""
TRACEWEAVE - Phase 19.6
MITRE ATT&CK Mapping Validation
"""

from typing import Any, Dict

from forensic_engine.incident.attack_mapping import (
    validate_attack_mapping,
)

from forensic_engine.incident.attack_mapping_provenance import (
    validate_attack_mapping_provenance,
)


def validate_complete_attack_mapping(
    mapping: Dict[str, Any],
) -> None:

    # Validate the complete base mapping.
    validate_attack_mapping(mapping)

    techniques = mapping["techniques"]

    technique_ids = set()
    total_links = 0

    for technique in techniques:

        technique_id = technique[
            "technique_id"
        ]

        # ---------------------------------------------
        # Technique uniqueness
        # ---------------------------------------------

        if technique_id in technique_ids:
            raise ValueError(
                f"Duplicate ATT&CK technique: "
                f"{technique_id}"
            )

        technique_ids.add(
            technique_id
        )

        # ---------------------------------------------
        # Technique mapping status
        # ---------------------------------------------

        if technique.get(
            "mapping_status"
        ) != "OBSERVED":

            raise ValueError(
                f"Technique {technique_id} "
                f"is not marked OBSERVED."
            )

        evidence_links = technique[
            "evidence_links"
        ]

        if not evidence_links:
            raise ValueError(
                f"Technique {technique_id} "
                f"has no evidence links."
            )

        # ---------------------------------------------
        # Validate evidence links
        # ---------------------------------------------

        link_ids = set()

        for link in evidence_links:

            link_id = link[
                "link_id"
            ]

            if link_id in link_ids:
                raise ValueError(
                    f"Duplicate evidence link: "
                    f"{link_id}"
                )

            link_ids.add(
                link_id
            )

            # Base evidence-link validation
            from forensic_engine.incident.technique_evidence_link import (
                validate_technique_evidence_link,
            )

            validate_technique_evidence_link(
                link
            )

            # -----------------------------------------
            # Technique consistency
            # -----------------------------------------

            linked_technique_id = link[
                "technique"
            ]["technique_id"]

            if linked_technique_id != (
                technique_id
            ):

                raise ValueError(
                    "Evidence link technique ID "
                    "does not match parent technique."
                )

            total_links += 1

    # ---------------------------------------------
    # Evidence-link count
    # ---------------------------------------------

    if mapping[
        "evidence_link_count"
    ] != total_links:

        raise ValueError(
            "Evidence-link count does not match "
            "actual number of evidence links."
        )

    # ---------------------------------------------
    # Mapping-level provenance
    # ---------------------------------------------

    provenance = mapping.get(
        "provenance"
    )

    if not isinstance(
        provenance,
        dict,
    ):

        raise ValueError(
            "ATT&CK mapping is missing provenance."
        )

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
            "ATT&CK mapping must not indicate "
            "network access."
        )


if __name__ == "__main__":

    from forensic_engine.incident.technique_evidence_link import (
        create_technique_evidence_link,
    )

    from forensic_engine.incident.attack_mapping import (
        build_attack_mapping,
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

    # Add mapping-level provenance required
    # by the final validation.
    mapping["provenance"] = {
        "construction_method":
            "EVIDENCE_LINK_AGGREGATION",
        "evidence_basis":
            "OBSERVED",
        "network_access_performed":
            False,
    }

    validate_complete_attack_mapping(
        mapping
    )

    print(
        "ATT&CK MAPPING VALIDATION: PASS"
    )
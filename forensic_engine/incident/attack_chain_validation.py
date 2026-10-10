"""
TRACEWEAVE - Phase 18.6
Attack Chain Validation
"""

from typing import Any, Dict

from forensic_engine.incident.attack_chain import (
    validate_attack_chain,
)

from forensic_engine.incident.attack_chain_provenance import (
    validate_attack_chain_provenance,
)


def validate_complete_attack_chain(
    chain: Dict[str, Any],
) -> None:

    # Validate the base attack-chain structure.
    validate_attack_chain(chain)

    stages = chain["stages"]

    stage_ids = set()

    for stage in stages:

        stage_id = stage["stage_id"]

        # -------------------------------------------------
        # Stage uniqueness
        # -------------------------------------------------

        if stage_id in stage_ids:
            raise ValueError(
                f"Duplicate attack stage ID: "
                f"{stage_id}"
            )

        stage_ids.add(stage_id)

        # -------------------------------------------------
        # Evidence validation
        # -------------------------------------------------

        evidence = stage.get(
            "evidence"
        )

        if not isinstance(
            evidence,
            dict,
        ):
            raise ValueError(
                f"Stage {stage_id} has invalid evidence."
            )

        supporting_events = evidence.get(
            "supporting_events"
        )

        if not supporting_events:
            raise ValueError(
                f"Stage {stage_id} has no "
                f"supporting events."
            )

        # -------------------------------------------------
        # Provenance validation
        # -------------------------------------------------

        provenance = stage.get(
            "provenance"
        )

        if not isinstance(
            provenance,
            dict,
        ):
            raise ValueError(
                f"Stage {stage_id} is missing "
                f"provenance."
            )

        validate_attack_chain_provenance(
            provenance
        )

        # -------------------------------------------------
        # Provenance → evidence consistency
        # -------------------------------------------------

        source_event = provenance[
            "source_event"
        ]

        supporting_event_ids = {
            event.get("event_id")
            for event in supporting_events
        }

        if source_event not in (
            supporting_event_ids
        ):
            raise ValueError(
                f"Provenance source event "
                f"{source_event} is not present "
                f"in stage evidence."
            )

        source_artifact = provenance[
            "source_artifact"
        ]

        evidence_artifacts = {
            event.get("source_artifact")
            for event in supporting_events
        }

        if source_artifact not in (
            evidence_artifacts
        ):
            raise ValueError(
                f"Provenance source artifact "
                f"{source_artifact} is not present "
                f"in stage evidence."
            )

        # -------------------------------------------------
        # Observation status
        # -------------------------------------------------

        if stage.get(
            "stage_status"
        ) != "OBSERVED":

            raise ValueError(
                f"Stage {stage_id} is not "
                f"marked OBSERVED."
            )

    # -----------------------------------------------------
    # Chain-level provenance
    # -----------------------------------------------------

    chain_provenance = chain[
        "provenance"
    ]

    if chain_provenance.get(
        "evidence_basis"
    ) != "OBSERVED":

        raise ValueError(
            "Attack chain evidence basis "
            "must be OBSERVED."
        )

    if chain_provenance.get(
        "network_access_performed"
    ) is not False:

        raise ValueError(
            "Attack chain must not indicate "
            "network access."
        )


if __name__ == "__main__":

    from forensic_engine.incident.attack_stage import (
        create_attack_stage,
    )

    from forensic_engine.incident.attack_chain import (
        build_attack_chain,
    )

    from forensic_engine.incident.attack_chain_provenance import (
        create_attack_chain_provenance,
        attach_stage_provenance,
    )

    stages = []

    stage = create_attack_stage(
        "DELIVERY",
        1,
        "Email received",
        {
            "event_id": "EVENT-001",
            "supporting_events": [
                {
                    "event_id": "EVENT-001",
                    "event_type":
                        "EMAIL_RECEIVED",
                    "timestamp":
                        "2026-10-08T10:00:00Z",
                    "source_artifact":
                        "email.eml",
                }
            ],
        },
    )

    provenance = create_attack_chain_provenance(
        "TIMELINE_EVENT_MAPPING",
        "EVENT-001",
        "email.eml",
        "email_header",
        "Delivery stage is supported "
        "by the observed email receipt event.",
    )

    attach_stage_provenance(
        stage,
        provenance,
    )

    stages.append(stage)

    chain = build_attack_chain(
        "TW-TEST-001",
        stages,
    )

    validate_complete_attack_chain(
        chain
    )

    print(
        "ATTACK CHAIN VALIDATION: PASS"
    )
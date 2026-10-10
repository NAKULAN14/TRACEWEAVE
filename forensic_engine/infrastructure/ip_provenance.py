"""
TRACEWEAVE - Phase 14.2.3
IP Relationship Provenance

Adds explicit provenance to DOMAIN -> IP infrastructure
relationships.

The relationship remains an observed fact derived from DNS
evidence. No ownership or maliciousness inference is made.
"""

from datetime import datetime, timezone
from typing import Any, Dict


def add_relationship_provenance(
    relationship: Dict[str, Any],
    dns_evidence_id: str,
    source_artifact: str = None,
    source_location: str = None,
) -> Dict[str, Any]:
    """
    Add explicit provenance to an infrastructure relationship.

    Args:
        relationship:
            Existing DOMAIN -> IP relationship.

        dns_evidence_id:
            Identifier linking the relationship back to
            the DNS evidence.

        source_artifact:
            Optional original evidence artifact.

        source_location:
            Optional location within the artifact.

    Returns:
        Relationship with provenance information.
    """

    if not isinstance(
        relationship,
        dict,
    ):
        raise ValueError(
            "Relationship must be a dictionary."
        )

    if not dns_evidence_id:
        raise ValueError(
            "dns_evidence_id cannot be empty."
        )

    relationship_copy = dict(
        relationship
    )

    relationship_copy[
        "provenance"
    ] = {
        "evidence_id":
            dns_evidence_id,

        "source_artifact":
            source_artifact,

        "source_location":
            source_location,

        "derivation_method":
            "DNS_EVIDENCE_CORRELATION",

        "relationship_status":
            "OBSERVED",

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "network_access_performed":
            False,
    }

    return relationship_copy


def validate_relationship_provenance(
    relationship: Dict[str, Any],
) -> bool:
    """
    Validate the provenance attached to a relationship.
    """

    provenance = relationship.get(
        "provenance"
    )

    if not isinstance(
        provenance,
        dict,
    ):
        return False

    required_fields = {
        "evidence_id",
        "derivation_method",
        "relationship_status",
        "created_at",
        "network_access_performed",
    }

    if not required_fields.issubset(
        provenance.keys()
    ):
        return False

    if (
        provenance[
            "derivation_method"
        ]
        != "DNS_EVIDENCE_CORRELATION"
    ):
        return False

    if (
        provenance[
            "relationship_status"
        ]
        != "OBSERVED"
    ):
        return False

    if (
        provenance[
            "network_access_performed"
        ]
        is not False
    ):
        return False

    return True
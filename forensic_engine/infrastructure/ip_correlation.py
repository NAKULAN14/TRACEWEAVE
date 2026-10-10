"""
TRACEWEAVE - Phase 14.2.1
IP Infrastructure Correlation

Represents observed relationships between domains and IP addresses
obtained from DNS evidence.

This module does not determine ownership or maliciousness.
"""

from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Any, Dict


SUPPORTED_IP_RECORD_TYPES = {
    "A",
    "AAAA",
}


def validate_ip(value: str) -> str:
    """
    Validate and normalize an IP address.
    """

    try:
        return str(ip_address(value))
    except ValueError as exc:
        raise ValueError(
            f"Invalid IP address: {value}"
        ) from exc


def create_ip_relationship(
    domain: str,
    ip_value: str,
    record_type: str,
    dns_provider: str,
) -> Dict[str, Any]:
    """
    Create an observed DOMAIN -> IP relationship.
    """

    normalized_domain = (
        domain.strip()
        .lower()
        .rstrip(".")
    )

    normalized_ip = validate_ip(
        ip_value
    )

    normalized_record_type = (
        record_type.upper()
    )

    if normalized_record_type not in (
        SUPPORTED_IP_RECORD_TYPES
    ):
        raise ValueError(
            f"Unsupported IP DNS record type: "
            f"{record_type}"
        )

    return {
        "relationship_type": "RESOLVES_TO",

        "source": {
            "type": "DOMAIN",
            "value": normalized_domain,
        },

        "target": {
            "type": "IP",
            "value": normalized_ip,
        },

        "evidence": {
            "record_type":
                normalized_record_type,

            "method": "DNS_RESOLUTION",

            "provider": dns_provider,

            "confidence": "OBSERVED",
        },

        "observed_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "network_access_performed": False,
    }
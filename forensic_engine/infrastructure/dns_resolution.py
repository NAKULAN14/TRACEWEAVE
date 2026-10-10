"""
TRACEWEAVE - Phase 14.1.3
DNS Resolution Evidence + Provenance

Converts DNS provider results into a standardized
forensic evidence record.

No maliciousness verdict is produced here.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from forensic_engine.infrastructure.dns_provider import DNSProvider


SUPPORTED_RECORD_TYPES = {
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "TXT",
}


def normalize_domain(domain: str) -> str:
    """
    Normalize a domain for DNS evidence collection.
    """

    normalized = (
        domain.strip()
        .lower()
        .rstrip(".")
    )

    if not normalized:
        raise ValueError(
            "Domain cannot be empty."
        )

    return normalized


def resolve_dns(
    provider: DNSProvider,
    domain: str,
) -> Dict[str, Any]:
    """
    Resolve a domain and create a standardized
    TRACEWEAVE DNS evidence record.
    """

    normalized_domain = normalize_domain(
        domain
    )

    provider_result = provider.resolve(
        normalized_domain
    )

    status = provider_result.get(
        "status"
    )

    if status not in {
        "RESOLVED",
        "NOT_FOUND",
    }:
        raise ValueError(
            f"Invalid DNS provider status: {status}"
        )

    records = provider_result.get(
        "records",
        []
    )

    if not isinstance(records, list):
        raise ValueError(
            "DNS records must be a list."
        )

    normalized_records = []

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            raise ValueError(
                "Each DNS record must be an object."
            )

        record_type = str(
            record.get(
                "record_type",
                ""
            )
        ).upper()

        value = record.get(
            "value"
        )

        if record_type not in SUPPORTED_RECORD_TYPES:
            raise ValueError(
                f"Unsupported DNS record type: {record_type}"
            )

        if not value:
            raise ValueError(
                "DNS record value cannot be empty."
            )

        normalized_records.append(
            {
                "record_type": record_type,
                "value": str(value),
            }
        )

    return {
        "domain": normalized_domain,

        "resolution": {
            "status": status,
            "records": normalized_records,
        },

        "provenance": {
            "provider": provider_result.get(
                "provider"
            ),
            "method": "DNS_RESOLUTION",
            "observed_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "network_access_performed":
                provider_result.get(
                    "network_access_performed",
                    False,
                ),
        },
    }


def main() -> None:

    import argparse
    import json

    from forensic_engine.infrastructure.static_dns_provider import (
        StaticDNSProvider,
    )

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE DNS resolution evidence"
    )

    parser.add_argument(
        "domain",
        help="Domain to resolve",
    )

    args = parser.parse_args()

    provider = StaticDNSProvider()

    result = resolve_dns(
        provider,
        args.domain,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
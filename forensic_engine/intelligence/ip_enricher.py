"""
TRACEWEAVE - Phase 13.4
IP Reputation Enrichment

Offline IP reputation enrichment using the existing
LocalThreatIntelligenceProvider.
"""

import argparse
import json
import sys
from ipaddress import IPv4Address, AddressValueError
from typing import Any, Dict

from forensic_engine.intelligence.local_provider import (
    LocalThreatIntelligenceProvider,
)


def validate_ipv4(value: str) -> str:
    """Validate and normalize an IPv4 address."""

    try:
        return str(IPv4Address(value))
    except AddressValueError as exc:
        raise ValueError(
            f"Invalid IPv4 address: {value}"
        ) from exc


def enrich_ip(
    provider: LocalThreatIntelligenceProvider,
    ip_address: str,
) -> Dict[str, Any]:
    """
    Enrich an IPv4 IOC using the existing local TI provider.
    """

    normalized_ip = validate_ipv4(ip_address)

    enrichment = provider.lookup(
        ioc_type="IPV4",
        value=normalized_ip,
    )

    return {
        "ioc_type": "IPV4",
        "value": normalized_ip,
        "enrichment": enrichment,
        "network_access_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TRACEWEAVE IP reputation enrichment"
    )

    parser.add_argument(
        "ip_address",
        help="IPv4 address to enrich",
    )

    args = parser.parse_args()

    try:
        # Use the existing provider exactly as implemented
        provider = LocalThreatIntelligenceProvider()

        result = enrich_ip(
            provider=provider,
            ip_address=args.ip_address,
        )

        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        return 0

    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": str(exc),
                    "network_access_performed": False,
                },
                indent=2,
            ),
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
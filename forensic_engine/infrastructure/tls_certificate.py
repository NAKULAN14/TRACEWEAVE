"""
TRACEWEAVE - Phase 14.3.3
TLS Certificate Evidence + Provenance

Converts TLS certificate provider results into a standardized
forensic evidence record.

No maliciousness verdict is produced here.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from forensic_engine.infrastructure.tls_provider import (
    TLSCertificateProvider,
)


def normalize_domain(domain: str) -> str:
    """Normalize a domain name."""

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


def get_certificate_evidence(
    provider: TLSCertificateProvider,
    domain: str,
) -> Dict[str, Any]:
    """
    Retrieve and standardize TLS certificate evidence.
    """

    normalized_domain = normalize_domain(
        domain
    )

    provider_result = provider.get_certificate(
        normalized_domain
    )

    status = provider_result.get(
        "status"
    )

    if status not in {
        "FOUND",
        "NOT_FOUND",
    }:
        raise ValueError(
            f"Invalid TLS provider status: {status}"
        )

    certificate = provider_result.get(
        "certificate"
    )

    if status == "FOUND":

        if not isinstance(
            certificate,
            dict,
        ):
            raise ValueError(
                "Certificate data must be an object."
            )

        required_fields = {
            "certificate_id",
            "subject",
            "issuer",
            "serial_number",
            "not_before",
            "not_after",
            "fingerprint_sha256",
            "san",
        }

        missing = (
            required_fields
            - set(certificate.keys())
        )

        if missing:
            raise ValueError(
                f"Missing certificate fields: "
                f"{sorted(missing)}"
            )

        if not isinstance(
            certificate["san"],
            list,
        ):
            raise ValueError(
                "Certificate SAN must be a list."
            )

    elif status == "NOT_FOUND":
        certificate = None

    return {
        "domain": normalized_domain,

        "certificate_status": status,

        "certificate": certificate,

        "provenance": {
            "provider":
                provider_result.get(
                    "provider"
                ),

            "method":
                "TLS_CERTIFICATE_COLLECTION",

            "observed_at":
                datetime.now(
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

    from forensic_engine.infrastructure.static_tls_provider import (
        StaticTLSCertificateProvider,
    )

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE TLS certificate evidence"
        )
    )

    parser.add_argument(
        "domain",
        help="Domain to inspect",
    )

    args = parser.parse_args()

    provider = StaticTLSCertificateProvider()

    result = get_certificate_evidence(
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
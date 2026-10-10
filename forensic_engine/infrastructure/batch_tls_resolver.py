"""
TRACEWEAVE - Phase 14.3.5
Batch TLS Certificate Evidence

Reads DOMAIN IOCs from Phase 12 and collects TLS certificate
evidence using the offline StaticTLSCertificateProvider.

No network access is performed.
"""

import csv
import json
import os
from typing import Any, Dict, List

from forensic_engine.infrastructure.static_tls_provider import (
    StaticTLSCertificateProvider,
)

from forensic_engine.infrastructure.tls_certificate import (
    get_certificate_evidence,
)


INPUT_PATH = os.path.join(
    "reports",
    "phase12",
    "deduplicated_iocs.json",
)

OUTPUT_DIR = os.path.join(
    "reports",
    "phase14",
    "tls_certificates",
)

JSON_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "tls_evidence.json",
)

CSV_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "tls_evidence.csv",
)

SUMMARY_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "batch_summary.json",
)


def load_domain_iocs(
    path: str,
) -> List[Dict[str, Any]]:
    """Load DOMAIN IOCs from Phase 12."""

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Expected Phase 12 IOC object."
        )

    iocs = data.get("iocs")

    if not isinstance(iocs, list):
        raise ValueError(
            "Phase 12 file does not contain an 'iocs' list."
        )

    return [
        ioc
        for ioc in iocs
        if str(
            ioc.get("ioc_type", "")
        ).upper() == "DOMAIN"
    ]


def write_json(
    path: str,
    data: Any,
) -> None:

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
        )


def write_csv(
    path: str,
    records: List[Dict[str, Any]],
) -> None:

    fieldnames = [
        "domain",
        "status",
        "certificate_id",
        "fingerprint_sha256",
        "subject",
        "issuer",
        "serial_number",
        "provider",
        "method",
        "observed_at",
        "network_access_performed",
        "observation_count",
    ]

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records:

            if "tls_evidence" not in record:
                continue

            ioc = record["ioc"]
            evidence = record[
                "tls_evidence"
            ]

            certificate = (
                evidence.get(
                    "certificate"
                )
                or {}
            )

            provenance = evidence.get(
                "provenance",
                {}
            )

            writer.writerow(
                {
                    "domain":
                        evidence.get(
                            "domain"
                        ),

                    "status":
                        evidence.get(
                            "certificate_status"
                        ),

                    "certificate_id":
                        certificate.get(
                            "certificate_id"
                        ),

                    "fingerprint_sha256":
                        certificate.get(
                            "fingerprint_sha256"
                        ),

                    "subject":
                        certificate.get(
                            "subject"
                        ),

                    "issuer":
                        certificate.get(
                            "issuer"
                        ),

                    "serial_number":
                        certificate.get(
                            "serial_number"
                        ),

                    "provider":
                        provenance.get(
                            "provider"
                        ),

                    "method":
                        provenance.get(
                            "method"
                        ),

                    "observed_at":
                        provenance.get(
                            "observed_at"
                        ),

                    "network_access_performed":
                        provenance.get(
                            "network_access_performed"
                        ),

                    "observation_count":
                        ioc.get(
                            "observation_count"
                        ),
                }
            )


def main() -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    provider = StaticTLSCertificateProvider()

    domain_iocs = load_domain_iocs(
        INPUT_PATH
    )

    results = []

    found_count = 0
    not_found_count = 0
    error_count = 0

    for ioc in domain_iocs:

        domain = ioc.get(
            "canonical_value"
        )

        try:

            tls_evidence = (
                get_certificate_evidence(
                    provider,
                    domain,
                )
            )

            results.append(
                {
                    "ioc": ioc,
                    "tls_evidence":
                        tls_evidence,
                }
            )

            status = tls_evidence.get(
                "certificate_status"
            )

            if status == "FOUND":
                found_count += 1

            elif status == "NOT_FOUND":
                not_found_count += 1

        except Exception as exc:

            error_count += 1

            results.append(
                {
                    "ioc": ioc,
                    "error": str(exc),
                }
            )

    summary = {
        "input": INPUT_PATH,
        "total_domain_iocs": len(
            domain_iocs
        ),
        "processed": (
            len(domain_iocs)
            - error_count
        ),
        "found": found_count,
        "not_found": not_found_count,
        "errors": error_count,
        "network_access_performed": False,
    }

    write_json(
        JSON_OUTPUT,
        results,
    )

    write_csv(
        CSV_OUTPUT,
        results,
    )

    write_json(
        SUMMARY_OUTPUT,
        summary,
    )

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
"""
TRACEWEAVE - Phase 14.1.4
Batch DNS Evidence Processing

Reads DOMAIN IOCs from Phase 12 and resolves them using
the offline StaticDNSProvider.
"""

import csv
import json
import os
from typing import Any, Dict, List

from forensic_engine.infrastructure.static_dns_provider import (
    StaticDNSProvider,
)

from forensic_engine.infrastructure.dns_resolution import (
    resolve_dns,
)


INPUT_PATH = os.path.join(
    "reports",
    "phase12",
    "deduplicated_iocs.json",
)

OUTPUT_DIR = os.path.join(
    "reports",
    "phase14",
    "dns_resolution",
)

JSON_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "dns_evidence.json",
)

CSV_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "dns_evidence.csv",
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
        "record_count",
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

            dns = record[
                "dns_evidence"
            ]

            resolution = dns[
                "resolution"
            ]

            provenance = dns[
                "provenance"
            ]

            writer.writerow(
                {
                    "domain":
                        dns.get(
                            "domain"
                        ),

                    "status":
                        resolution.get(
                            "status"
                        ),

                    "record_count":
                        len(
                            resolution.get(
                                "records",
                                [],
                            )
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
                        record[
                            "ioc"
                        ].get(
                            "observation_count"
                        ),
                }
            )


def main() -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    provider = StaticDNSProvider()

    domain_iocs = load_domain_iocs(
        INPUT_PATH
    )

    results = []

    resolved_count = 0
    not_found_count = 0
    error_count = 0

    for ioc in domain_iocs:

        domain = ioc.get(
            "canonical_value"
        )

        try:

            dns_evidence = resolve_dns(
                provider,
                domain,
            )

            results.append(
                {
                    "ioc": ioc,
                    "dns_evidence":
                        dns_evidence,
                }
            )

            status = (
                dns_evidence[
                    "resolution"
                ][
                    "status"
                ]
            )

            if status == "RESOLVED":
                resolved_count += 1

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
        "resolved": resolved_count,
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
        [
            result
            for result in results
            if "dns_evidence" in result
        ],
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
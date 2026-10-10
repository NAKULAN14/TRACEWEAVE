"""
TRACEWEAVE - Phase 13.7
Batch Threat Intelligence Enrichment

Reads deduplicated IOCs from Phase 12 and enriches them
using the offline LocalThreatIntelligenceProvider.

Preserves the complete Phase 12 IOC record and observations.
"""

import csv
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from forensic_engine.intelligence.local_provider import (
    LocalThreatIntelligenceProvider,
)

from forensic_engine.intelligence.enrichment_result import (
    create_enrichment_result,
)


INPUT_PATH = os.path.join(
    "reports",
    "phase12",
    "deduplicated_iocs.json",
)

OUTPUT_DIR = os.path.join(
    "reports",
    "phase13",
    "batch_enrichment",
)

JSON_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "enriched_iocs.json",
)

CSV_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "enriched_iocs.csv",
)

SUMMARY_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "batch_summary.json",
)


SUPPORTED_TYPES = {
    "URL",
    "DOMAIN",
    "EMAIL",
    "IPV4",
    "MD5",
    "SHA1",
    "SHA256",
}


def load_iocs(path: str) -> List[Dict[str, Any]]:
    """Load deduplicated IOC records from Phase 12."""

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Expected Phase 12 deduplicated IOC object."
        )

    iocs = data.get("iocs")

    if not isinstance(iocs, list):
        raise ValueError(
            "Phase 12 file does not contain an 'iocs' list."
        )

    return iocs


def get_source_information(
    ioc: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract provenance from the first Phase 12 observation.
    """

    observations = ioc.get("observations", [])

    if not observations:
        return {
            "source_artifact": None,
            "source_location": None,
        }

    first_observation = observations[0]

    evidence = first_observation.get(
        "observation",
        {}
    ).get(
        "evidence",
        {}
    )

    return {
        "source_artifact": evidence.get(
            "artifact"
        ),
        "source_location": evidence.get(
            "source_location"
        ),
    }


def enrich_ioc(
    provider: LocalThreatIntelligenceProvider,
    ioc: Dict[str, Any],
) -> Dict[str, Any]:
    """Enrich one Phase 12 deduplicated IOC."""

    ioc_type = str(
        ioc.get("ioc_type", "")
    ).upper()

    canonical_value = ioc.get(
        "canonical_value"
    )

    if ioc_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported IOC type: {ioc_type}"
        )

    if not canonical_value:
        raise ValueError(
            "IOC has no canonical_value."
        )

    source = get_source_information(ioc)

    enrichment = provider.lookup(
        ioc_type=ioc_type,
        value=canonical_value,
    )

    enrichment_result = create_enrichment_result(
        ioc_type=ioc_type,
        value=canonical_value,
        enrichment=enrichment,
        source_artifact=source[
            "source_artifact"
        ],
        source_location=source[
            "source_location"
        ],
    )

    return {
        "ioc": ioc,
        "enrichment_result": enrichment_result,
    }


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
        "enrichment_id",
        "ioc_type",
        "value",
        "observation_count",
        "provider",
        "status",
        "source_artifact",
        "source_location",
        "enriched_at",
        "network_access_performed",
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

            if "enrichment_result" not in record:
                continue

            ioc = record["ioc"]
            result = record[
                "enrichment_result"
            ]

            enrichment = result.get(
                "enrichment",
                {},
            )

            provenance = result.get(
                "provenance",
                {},
            )

            writer.writerow(
                {
                    "enrichment_id":
                        result.get(
                            "enrichment_id"
                        ),

                    "ioc_type":
                        result.get(
                            "ioc_type"
                        ),

                    "value":
                        result.get(
                            "value"
                        ),

                    "observation_count":
                        ioc.get(
                            "observation_count"
                        ),

                    "provider":
                        enrichment.get(
                            "provider"
                        ),

                    "status":
                        enrichment.get(
                            "status"
                        ),

                    "source_artifact":
                        provenance.get(
                            "source_artifact"
                        ),

                    "source_location":
                        provenance.get(
                            "source_location"
                        ),

                    "enriched_at":
                        provenance.get(
                            "enriched_at"
                        ),

                    "network_access_performed":
                        result.get(
                            "network_access_performed"
                        ),
                }
            )


def main() -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    provider = LocalThreatIntelligenceProvider()

    iocs = load_iocs(
        INPUT_PATH
    )

    enriched_records = []

    found_count = 0
    not_found_count = 0
    error_count = 0

    type_counts: Dict[str, int] = {}

    for ioc in iocs:

        try:

            record = enrich_ioc(
                provider,
                ioc,
            )

            enriched_records.append(
                record
            )

            result = record[
                "enrichment_result"
            ]

            ioc_type = result[
                "ioc_type"
            ]

            status = result[
                "enrichment"
            ].get(
                "status"
            )

            type_counts[ioc_type] = (
                type_counts.get(
                    ioc_type,
                    0,
                )
                + 1
            )

            if status == "FOUND":
                found_count += 1

            elif status == "NOT_FOUND":
                not_found_count += 1

        except Exception as exc:

            error_count += 1

            enriched_records.append(
                {
                    "ioc": ioc,
                    "error": str(exc),
                }
            )

    summary = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "input": INPUT_PATH,

        "total_iocs": len(iocs),

        "enriched": (
            len(enriched_records)
            - error_count
        ),

        "found": found_count,

        "not_found": not_found_count,

        "errors": error_count,

        "ioc_type_counts": type_counts,

        "network_access_performed": False,
    }

    write_json(
        JSON_OUTPUT,
        enriched_records,
    )

    write_csv(
        CSV_OUTPUT,
        enriched_records,
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
"""
TRACEWEAVE - Phase 13.8
Threat Intelligence Validation

Validates Phase 13 batch enrichment results.

Checks:
- Required result structure
- Supported IOC types
- Enrichment status
- Provider presence
- Provenance
- Network-access flag
- No duplicate enrichment identities
- Original IOC preservation
"""

import json
import os
from typing import Any, Dict, List, Tuple


INPUT_PATH = os.path.join(
    "reports",
    "phase13",
    "batch_enrichment",
    "enriched_iocs.json",
)

OUTPUT_PATH = os.path.join(
    "reports",
    "phase13",
    "batch_enrichment",
    "validation_report.json",
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

SUPPORTED_STATUSES = {
    "FOUND",
    "NOT_FOUND",
}


def load_results(
    path: str,
) -> List[Dict[str, Any]]:
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Expected enrichment results to be a list."
        )

    return data


def validate_record(
    record: Dict[str, Any],
) -> Tuple[bool, List[str]]:

    errors = []

    if "ioc" not in record:
        errors.append(
            "Missing original IOC record."
        )

    if "enrichment_result" not in record:
        errors.append(
            "Missing enrichment_result."
        )
        return False, errors

    result = record[
        "enrichment_result"
    ]

    required_fields = {
        "enrichment_id",
        "ioc_type",
        "value",
        "enrichment",
        "provenance",
        "network_access_performed",
    }

    missing = (
        required_fields
        - set(result.keys())
    )

    if missing:
        errors.append(
            f"Missing fields: {sorted(missing)}"
        )

    ioc_type = result.get(
        "ioc_type"
    )

    if ioc_type not in SUPPORTED_TYPES:
        errors.append(
            f"Unsupported IOC type: {ioc_type}"
        )

    value = result.get("value")

    if not isinstance(
        value,
        str,
    ) or not value.strip():
        errors.append(
            "IOC value is empty or invalid."
        )

    enrichment = result.get(
        "enrichment"
    )

    if not isinstance(
        enrichment,
        dict,
    ):
        errors.append(
            "Enrichment must be an object."
        )
    else:

        provider = enrichment.get(
            "provider"
        )

        if not provider:
            errors.append(
                "Missing enrichment provider."
            )

        status = enrichment.get(
            "status"
        )

        if status not in SUPPORTED_STATUSES:
            errors.append(
                f"Invalid enrichment status: {status}"
            )

    provenance = result.get(
        "provenance"
    )

    if not isinstance(
        provenance,
        dict,
    ):
        errors.append(
            "Missing or invalid provenance."
        )
    else:

        if "enriched_at" not in provenance:
            errors.append(
                "Missing enrichment timestamp."
            )

    if result.get(
        "network_access_performed"
    ) is not False:

        errors.append(
            "Network access flag is not False."
        )

    # Verify original IOC preservation
    original_ioc = record.get(
        "ioc",
        {}
    )

    original_type = original_ioc.get(
        "ioc_type"
    )

    original_value = original_ioc.get(
        "canonical_value"
    )

    if original_type != ioc_type:
        errors.append(
            "Original IOC type was not preserved."
        )

    if original_value != value:
        errors.append(
            "Original canonical IOC value was not preserved."
        )

    return (
        len(errors) == 0,
        errors,
    )


def main() -> None:

    results = load_results(
        INPUT_PATH
    )

    total = len(results)

    valid = 0
    invalid = 0

    validation_errors = []

    identities = set()
    duplicate_identities = []

    status_counts = {
        "FOUND": 0,
        "NOT_FOUND": 0,
    }

    type_counts: Dict[str, int] = {}

    for index, record in enumerate(
        results
    ):

        success, errors = validate_record(
            record
        )

        if success:
            valid += 1
        else:
            invalid += 1

            validation_errors.append(
                {
                    "record_index": index,
                    "errors": errors,
                }
            )

        result = record.get(
            "enrichment_result",
            {}
        )

        ioc_type = result.get(
            "ioc_type"
        )

        value = result.get(
            "value"
        )

        if ioc_type and value:

            identity = (
                ioc_type,
                value,
            )

            if identity in identities:
                duplicate_identities.append(
                    {
                        "ioc_type": ioc_type,
                        "value": value,
                    }
                )

            identities.add(identity)

            type_counts[ioc_type] = (
                type_counts.get(
                    ioc_type,
                    0,
                )
                + 1
            )

        status = result.get(
            "enrichment",
            {},
        ).get(
            "status"
        )

        if status in status_counts:
            status_counts[status] += 1

    report = {
        "input": INPUT_PATH,
        "total_records": total,
        "valid_records": valid,
        "invalid_records": invalid,
        "validation_status": (
            "PASS"
            if invalid == 0
            else "FAIL"
        ),
        "status_counts": status_counts,
        "ioc_type_counts": type_counts,
        "duplicate_enrichment_identities":
            duplicate_identities,
        "network_access_performed": False,
        "errors": validation_errors,
    }

    os.makedirs(
        os.path.dirname(
            OUTPUT_PATH
        ),
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
        )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
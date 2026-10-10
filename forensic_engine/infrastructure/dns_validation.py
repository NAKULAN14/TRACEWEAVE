"""
TRACEWEAVE - Phase 14.1.5
DNS Evidence Validation

Validates Phase 14.1 DNS batch results.

Checks:
- Original DOMAIN IOC preservation
- Domain normalization
- DNS resolution status
- DNS record structure
- Provider provenance
- Observation timestamp
- Network-access flag
- Duplicate domain identities
"""

import json
import os
from typing import Any, Dict, List, Tuple


INPUT_PATH = os.path.join(
    "reports",
    "phase14",
    "dns_resolution",
    "dns_evidence.json",
)

OUTPUT_PATH = os.path.join(
    "reports",
    "phase14",
    "dns_resolution",
    "validation_report.json",
)


SUPPORTED_RECORD_TYPES = {
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "TXT",
}

SUPPORTED_STATUSES = {
    "RESOLVED",
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
            "Expected DNS evidence to be a list."
        )

    return data


def validate_record(
    record: Dict[str, Any],
) -> Tuple[bool, List[str]]:

    errors = []

    if "ioc" not in record:
        errors.append(
            "Missing original IOC."
        )

    if "dns_evidence" not in record:
        errors.append(
            "Missing dns_evidence."
        )
        return False, errors

    ioc = record["ioc"]
    dns = record["dns_evidence"]

    # --------------------------------------------------
    # DNS top-level structure
    # --------------------------------------------------

    domain = dns.get("domain")

    if not isinstance(
        domain,
        str,
    ) or not domain:

        errors.append(
            "Invalid or missing domain."
        )

    normalized_domain = (
        domain.strip()
        .lower()
        .rstrip(".")
        if isinstance(domain, str)
        else None
    )

    if domain != normalized_domain:
        errors.append(
            "Domain is not normalized."
        )

    # --------------------------------------------------
    # Original IOC preservation
    # --------------------------------------------------

    if ioc.get("ioc_type") != "DOMAIN":
        errors.append(
            "Original IOC is not a DOMAIN IOC."
        )

    original_value = ioc.get(
        "canonical_value"
    )

    if original_value != domain:
        errors.append(
            "Original canonical domain was not preserved."
        )

    # --------------------------------------------------
    # Resolution
    # --------------------------------------------------

    resolution = dns.get(
        "resolution"
    )

    if not isinstance(
        resolution,
        dict,
    ):
        errors.append(
            "Invalid resolution object."
        )
        resolution = {}

    status = resolution.get(
        "status"
    )

    if status not in SUPPORTED_STATUSES:
        errors.append(
            f"Invalid DNS status: {status}"
        )

    records = resolution.get(
        "records"
    )

    if not isinstance(
        records,
        list,
    ):
        errors.append(
            "DNS records must be a list."
        )
        records = []

    # --------------------------------------------------
    # DNS records
    # --------------------------------------------------

    for index, dns_record in enumerate(
        records
    ):

        if not isinstance(
            dns_record,
            dict,
        ):
            errors.append(
                f"Record {index} is not an object."
            )
            continue

        record_type = dns_record.get(
            "record_type"
        )

        value = dns_record.get(
            "value"
        )

        if record_type not in SUPPORTED_RECORD_TYPES:
            errors.append(
                f"Unsupported record type: "
                f"{record_type}"
            )

        if not isinstance(
            value,
            str,
        ) or not value:

            errors.append(
                f"Record {index} has invalid value."
            )

    # NOT_FOUND should not contain records
    if (
        status == "NOT_FOUND"
        and records
    ):
        errors.append(
            "NOT_FOUND result contains DNS records."
        )

    # RESOLVED should have at least one record
    if (
        status == "RESOLVED"
        and not records
    ):
        errors.append(
            "RESOLVED result contains no DNS records."
        )

    # --------------------------------------------------
    # Provenance
    # --------------------------------------------------

    provenance = dns.get(
        "provenance"
    )

    if not isinstance(
        provenance,
        dict,
    ):
        errors.append(
            "Missing or invalid provenance."
        )
        provenance = {}

    if not provenance.get(
        "provider"
    ):
        errors.append(
            "Missing DNS provider."
        )

    if provenance.get(
        "method"
    ) != "DNS_RESOLUTION":

        errors.append(
            "Invalid DNS collection method."
        )

    if not provenance.get(
        "observed_at"
    ):
        errors.append(
            "Missing DNS observation timestamp."
        )

    if provenance.get(
        "network_access_performed"
    ) is not False:

        errors.append(
            "Network access flag is not False."
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

    domains = set()
    duplicate_domains = []

    status_counts = {
        "RESOLVED": 0,
        "NOT_FOUND": 0,
    }

    record_type_counts: Dict[
        str,
        int,
    ] = {}

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

        dns = record.get(
            "dns_evidence",
            {}
        )

        domain = dns.get(
            "domain"
        )

        if domain:

            if domain in domains:
                duplicate_domains.append(
                    domain
                )

            domains.add(domain)

        resolution = dns.get(
            "resolution",
            {}
        )

        status = resolution.get(
            "status"
        )

        if status in status_counts:
            status_counts[status] += 1

        for dns_record in resolution.get(
            "records",
            [],
        ):

            record_type = dns_record.get(
                "record_type"
            )

            if record_type:
                record_type_counts[
                    record_type
                ] = (
                    record_type_counts.get(
                        record_type,
                        0,
                    )
                    + 1
                )

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
        "record_type_counts":
            record_type_counts,
        "duplicate_domains":
            duplicate_domains,
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
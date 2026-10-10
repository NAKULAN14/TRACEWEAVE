"""
TRACEWEAVE - Phase 14.2.5
IP Infrastructure Correlation Validation
"""

import json
import os
from typing import Any, Dict, List, Tuple


INPUT_PATH = os.path.join(
    "reports",
    "phase14",
    "ip_correlation",
    "dns_ip_relationships.json",
)

OUTPUT_PATH = os.path.join(
    "reports",
    "phase14",
    "ip_correlation",
    "validation_report.json",
)


def load_data(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Expected IP correlation output to be an object."
        )

    return data


def validate_relationship(
    relationship: Dict[str, Any],
) -> Tuple[bool, List[str]]:

    errors = []

    if relationship.get(
        "relationship_type"
    ) != "RESOLVES_TO":
        errors.append(
            "Invalid relationship type."
        )

    source = relationship.get(
        "source",
        {}
    )

    if source.get("type") != "DOMAIN":
        errors.append(
            "Source is not a DOMAIN."
        )

    if not source.get("value"):
        errors.append(
            "Source domain is missing."
        )

    target = relationship.get(
        "target",
        {}
    )

    if target.get("type") != "IP":
        errors.append(
            "Target is not an IP."
        )

    if not target.get("value"):
        errors.append(
            "Target IP is missing."
        )

    evidence = relationship.get(
        "evidence",
        {}
    )

    if evidence.get(
        "method"
    ) != "DNS_RESOLUTION":
        errors.append(
            "Invalid evidence method."
        )

    if evidence.get(
        "confidence"
    ) != "OBSERVED":
        errors.append(
            "Relationship confidence must be OBSERVED."
        )

    provenance = relationship.get(
        "provenance",
        {}
    )

    required_provenance = {
        "evidence_id",
        "derivation_method",
        "relationship_status",
        "created_at",
        "network_access_performed",
    }

    missing = (
        required_provenance
        - set(provenance.keys())
    )

    if missing:
        errors.append(
            f"Missing provenance fields: "
            f"{sorted(missing)}"
        )

    if provenance.get(
        "derivation_method"
    ) != "DNS_EVIDENCE_CORRELATION":
        errors.append(
            "Invalid derivation method."
        )

    if provenance.get(
        "relationship_status"
    ) != "OBSERVED":
        errors.append(
            "Relationship status is not OBSERVED."
        )

    if provenance.get(
        "network_access_performed"
    ) is not False:
        errors.append(
            "Provenance indicates network access."
        )

    if relationship.get(
        "network_access_performed"
    ) is not False:
        errors.append(
            "Relationship indicates network access."
        )

    return (
        len(errors) == 0,
        errors,
    )


def main() -> None:

    data = load_data(
        INPUT_PATH
    )

    relationships = data.get(
        "relationships",
        []
    )

    if not isinstance(
        relationships,
        list,
    ):
        raise ValueError(
            "Relationships must be a list."
        )

    valid = 0
    invalid = 0
    errors = []

    identities = set()
    duplicate_relationships = []

    for index, relationship in enumerate(
        relationships
    ):

        success, validation_errors = (
            validate_relationship(
                relationship
            )
        )

        if success:
            valid += 1
        else:
            invalid += 1

            errors.append(
                {
                    "relationship_index": index,
                    "errors": validation_errors,
                }
            )

        source = relationship.get(
            "source",
            {}
        )

        target = relationship.get(
            "target",
            {}
        )

        identity = (
            source.get("value"),
            target.get("value"),
        )

        if identity in identities:
            duplicate_relationships.append(
                {
                    "domain": source.get(
                        "value"
                    ),
                    "ip": target.get(
                        "value"
                    ),
                }
            )

        identities.add(identity)

    report = {
        "input": INPUT_PATH,
        "total_relationships": len(
            relationships
        ),
        "valid_relationships": valid,
        "invalid_relationships": invalid,
        "validation_status": (
            "PASS"
            if invalid == 0
            else "FAIL"
        ),
        "duplicate_relationships":
            duplicate_relationships,
        "network_access_performed": False,
        "errors": errors,
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
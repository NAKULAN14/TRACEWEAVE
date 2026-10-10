"""
TRACEWEAVE - Phase 14.3.6
TLS Certificate Correlation Validation
"""

import json
import os
import sys
from typing import Any, Dict, List


TLS_EVIDENCE_PATH = os.path.join(
    "reports",
    "phase14",
    "tls_certificates",
    "tls_evidence.json",
)

RELATIONSHIP_PATH = os.path.join(
    "reports",
    "phase14",
    "tls_correlation",
    "domain_certificate_relationships.json",
)


def load_json(path: str) -> Any:
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def validate_tls_evidence(
    data: Any,
) -> List[str]:

    errors = []

    if not isinstance(data, list):
        return ["TLS evidence must be a list."]

    for index, item in enumerate(data):

        prefix = f"Evidence[{index}]"

        if not isinstance(item, dict):
            errors.append(
                f"{prefix}: must be an object."
            )
            continue

        if "ioc" not in item:
            errors.append(
                f"{prefix}: missing original IOC."
            )

        evidence = item.get(
            "tls_evidence"
        )

        if evidence is None:
            if "error" not in item:
                errors.append(
                    f"{prefix}: missing TLS evidence."
                )
            continue

        required = [
            "domain",
            "certificate_status",
            "certificate",
            "provenance",
        ]

        for field in required:
            if field not in evidence:
                errors.append(
                    f"{prefix}: missing {field}."
                )

        status = evidence.get(
            "certificate_status"
        )

        if status not in {
            "FOUND",
            "NOT_FOUND",
        }:
            errors.append(
                f"{prefix}: invalid certificate status."
            )

        provenance = evidence.get(
            "provenance",
            {}
        )

        if provenance.get(
            "method"
        ) != "TLS_CERTIFICATE_COLLECTION":

            errors.append(
                f"{prefix}: invalid provenance method."
            )

        if provenance.get(
            "provider"
        ) != "STATIC_TLS":

            errors.append(
                f"{prefix}: invalid provider."
            )

        if provenance.get(
            "network_access_performed"
        ) is not False:

            errors.append(
                f"{prefix}: network access flag must be false."
            )

        if status == "FOUND":

            certificate = evidence.get(
                "certificate"
            )

            if not isinstance(
                certificate,
                dict,
            ):
                errors.append(
                    f"{prefix}: FOUND certificate must be an object."
                )
                continue

            required_certificate_fields = [
                "certificate_id",
                "subject",
                "issuer",
                "serial_number",
                "not_before",
                "not_after",
                "fingerprint_sha256",
                "san",
            ]

            for field in required_certificate_fields:
                if field not in certificate:
                    errors.append(
                        f"{prefix}: certificate missing {field}."
                    )

            fingerprint = certificate.get(
                "fingerprint_sha256",
                ""
            )

            if (
                not isinstance(fingerprint, str)
                or len(fingerprint) != 64
            ):
                errors.append(
                    f"{prefix}: invalid SHA-256 fingerprint."
                )

            if not isinstance(
                certificate.get("san"),
                list,
            ):
                errors.append(
                    f"{prefix}: SAN must be a list."
                )

        elif status == "NOT_FOUND":

            if evidence.get(
                "certificate"
            ) is not None:

                errors.append(
                    f"{prefix}: NOT_FOUND must have certificate=null."
                )

    return errors


def validate_relationships(
    data: Any,
) -> List[str]:

    errors = []

    if not isinstance(data, list):
        return [
            "Certificate relationships must be a list."
        ]

    seen = set()

    for index, relationship in enumerate(data):

        prefix = f"Relationship[{index}]"

        if not isinstance(
            relationship,
            dict,
        ):
            errors.append(
                f"{prefix}: must be an object."
            )
            continue

        if relationship.get(
            "relationship_type"
        ) != "PRESENTS_CERTIFICATE":

            errors.append(
                f"{prefix}: invalid relationship type."
            )

        source = relationship.get(
            "source",
            {}
        )

        target = relationship.get(
            "target",
            {}
        )

        if source.get("type") != "DOMAIN":
            errors.append(
                f"{prefix}: source must be DOMAIN."
            )

        if target.get(
            "type"
        ) != "TLS_CERTIFICATE":

            errors.append(
                f"{prefix}: target must be TLS_CERTIFICATE."
            )

        evidence = relationship.get(
            "evidence",
            {}
        )

        if evidence.get(
            "method"
        ) != "TLS_CERTIFICATE_COLLECTION":

            errors.append(
                f"{prefix}: invalid evidence method."
            )

        if evidence.get(
            "provider"
        ) != "STATIC_TLS":

            errors.append(
                f"{prefix}: invalid provider."
            )

        if evidence.get(
            "confidence"
        ) != "OBSERVED":

            errors.append(
                f"{prefix}: confidence must be OBSERVED."
            )

        if relationship.get(
            "network_access_performed"
        ) is not False:

            errors.append(
                f"{prefix}: network access must be false."
            )

        key = (
            source.get("value"),
            target.get("value"),
        )

        if key in seen:
            errors.append(
                f"{prefix}: duplicate relationship."
            )

        seen.add(key)

        certificate = relationship.get(
            "certificate",
            {}
        )

        fingerprint = certificate.get(
            "fingerprint_sha256",
            ""
        )

        if (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 64
        ):
            errors.append(
                f"{prefix}: invalid certificate fingerprint."
            )

    return errors


def main() -> None:

    all_errors = []

    if not os.path.exists(
        TLS_EVIDENCE_PATH
    ):
        all_errors.append(
            "TLS evidence file does not exist."
        )

    if not os.path.exists(
        RELATIONSHIP_PATH
    ):
        all_errors.append(
            "TLS relationship file does not exist."
        )

    if all_errors:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "errors": all_errors,
                },
                indent=2,
            )
        )
        sys.exit(1)

    evidence = load_json(
        TLS_EVIDENCE_PATH
    )
 
    relationships = load_json(
    RELATIONSHIP_PATH
)

        # Support the existing TRACEWEAVE relationship
# output format if it is wrapped in an object.
    if isinstance(relationships, dict):
        relationships = relationships.get(
            "relationships",
            []
    )

    all_errors.extend(
        validate_tls_evidence(
            evidence
        )
    )

    all_errors.extend(
        validate_relationships(
            relationships
        )
    )

    status = (
        "PASS"
        if not all_errors
        else "FAIL"
    )

    result = {
        "status": status,
        "tls_evidence_records": len(
            evidence
        ),
        "certificate_relationships": len(
            relationships
        ),
        "errors": all_errors,
        "network_access_performed": False,
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    if status == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
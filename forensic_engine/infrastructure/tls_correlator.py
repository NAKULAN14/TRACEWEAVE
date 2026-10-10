"""
TRACEWEAVE - Phase 14.3.4
Domain -> TLS Certificate Correlation

Creates observed DOMAIN -> TLS_CERTIFICATE relationships
from TLS certificate evidence.

No ownership or maliciousness inference is made.
No network access is performed.
"""

import json
import os
from typing import Any, Dict, List


INPUT_PATH = os.path.join(
    "reports",
    "phase14",
    "tls_certificates",
    "tls_evidence.json",
)

OUTPUT_DIR = os.path.join(
    "reports",
    "phase14",
    "tls_correlation",
)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "domain_certificate_relationships.json",
)


def load_tls_evidence(
    path: str,
) -> List[Dict[str, Any]]:
    """Load TLS certificate evidence."""

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Expected TLS evidence to be a list."
        )

    return data


def create_certificate_relationship(
    tls_record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create a DOMAIN -> TLS_CERTIFICATE relationship.
    """

    evidence = tls_record.get(
        "tls_evidence"
    )

    if not evidence:
        raise ValueError(
            "Missing TLS evidence."
        )

    if evidence.get(
        "certificate_status"
    ) != "FOUND":

        raise ValueError(
            "Cannot create certificate relationship "
            "for a NOT_FOUND result."
        )

    domain = evidence.get(
        "domain"
    )

    certificate = evidence.get(
        "certificate"
    )

    if not domain:
        raise ValueError(
            "Missing domain."
        )

    if not isinstance(
        certificate,
        dict,
    ):
        raise ValueError(
            "Certificate must be an object."
        )

    certificate_id = certificate.get(
        "certificate_id"
    )

    fingerprint = certificate.get(
        "fingerprint_sha256"
    )

    if not certificate_id:
        raise ValueError(
            "Missing certificate ID."
        )

    if not fingerprint:
        raise ValueError(
            "Missing certificate fingerprint."
        )

    provenance = evidence.get(
        "provenance",
        {}
    )

    return {
        "relationship_type":
            "PRESENTS_CERTIFICATE",

        "source": {
            "type": "DOMAIN",
            "value": domain,
        },

        "target": {
            "type": "TLS_CERTIFICATE",
            "value": certificate_id,
        },

        "certificate": {
            "fingerprint_sha256":
                fingerprint,

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
        },

        "evidence": {
            "method":
                "TLS_CERTIFICATE_COLLECTION",

            "provider":
                provenance.get(
                    "provider"
                ),

            "confidence":
                "OBSERVED",
        },

        "observed_at":
            provenance.get(
                "observed_at"
            ),

        "network_access_performed":
            False,
    }


def main() -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    tls_records = load_tls_evidence(
        INPUT_PATH
    )

    relationships = []

    for record in tls_records:

        try:

            relationship = (
                create_certificate_relationship(
                    record
                )
            )

            relationships.append(
                relationship
            )

        except ValueError:
            # NOT_FOUND or incomplete records
            # do not produce relationships.
            continue

    output = {
        "input": INPUT_PATH,

        "relationship_count":
            len(relationships),

        "network_access_performed":
            False,

        "relationships":
            relationships,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
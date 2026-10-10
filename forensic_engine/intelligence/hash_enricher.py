

import argparse
import hashlib
import json
import sys
from typing import Any, Dict

from forensic_engine.intelligence.local_provider import (
    LocalThreatIntelligenceProvider,
)


SUPPORTED_HASH_TYPES = {
    "MD5": 32,
    "SHA1": 40,
    "SHA256": 64,
}


def detect_hash_type(value: str) -> str:
    """
    Detect the hash type based on hexadecimal length.
    """

    normalized = value.strip().lower()

    if len(normalized) == 32:
        hash_type = "MD5"
    elif len(normalized) == 40:
        hash_type = "SHA1"
    elif len(normalized) == 64:
        hash_type = "SHA256"
    else:
        raise ValueError(
            "Unsupported hash length. "
            "Expected MD5 (32), SHA1 (40), or SHA256 (64) hexadecimal characters."
        )

    if any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError(
            "Hash contains non-hexadecimal characters."
        )

    return hash_type


def normalize_hash(value: str) -> str:
    """
    Normalize a hash value to lowercase.
    """

    return value.strip().lower()


def enrich_hash(
    provider: LocalThreatIntelligenceProvider,
    hash_value: str,
) -> Dict[str, Any]:
    """
    Enrich a hash IOC using the existing local TI provider.
    """

    normalized_hash = normalize_hash(hash_value)

    hash_type = detect_hash_type(normalized_hash)

    enrichment = provider.lookup(
        ioc_type=hash_type,
        value=normalized_hash,
    )

    return {
        "ioc_type": hash_type,
        "value": normalized_hash,
        "enrichment": enrichment,
        "network_access_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TRACEWEAVE hash reputation enrichment"
    )

    parser.add_argument(
        "hash_value",
        help="MD5, SHA1, or SHA256 hash",
    )

    args = parser.parse_args()

    try:
        provider = LocalThreatIntelligenceProvider()

        result = enrich_hash(
            provider=provider,
            hash_value=args.hash_value,
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
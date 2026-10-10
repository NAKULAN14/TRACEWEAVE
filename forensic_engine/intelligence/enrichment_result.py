"""
TRACEWEAVE - Phase 13.6
Unified Threat Intelligence Enrichment Result

Provides a common result structure for:
- URL
- DOMAIN
- IPV4
- MD5
- SHA1
- SHA256

The structure preserves:
- IOC identity
- Provider information
- Enrichment status
- Source/provenance
- Network-access status
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


SUPPORTED_IOC_TYPES = {
    "URL",
    "DOMAIN",
    "EMAIL",
    "IPV4",
    "MD5",
    "SHA1",
    "SHA256",
}


def create_enrichment_result(
    ioc_type: str,
    value: str,
    enrichment: Dict[str, Any],
    source_artifact: Optional[str] = None,
    source_location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a unified TRACEWEAVE enrichment result.

    Args:
        ioc_type:
            IOC type being enriched.

        value:
            Normalized IOC value.

        enrichment:
            Result returned by the threat intelligence provider.

        source_artifact:
            Optional source artifact path or identifier.

        source_location:
            Optional location within the artifact.

    Returns:
        Structured enrichment result.
    """

    normalized_type = ioc_type.upper()

    if normalized_type not in SUPPORTED_IOC_TYPES:
        raise ValueError(
            f"Unsupported IOC type: {ioc_type}"
        )

    if not value or not value.strip():
        raise ValueError(
            "IOC value cannot be empty."
        )

    return {
        "enrichment_id": str(uuid.uuid4()),
        "ioc_type": normalized_type,
        "value": value,
        "enrichment": enrichment,
        "provenance": {
            "source_artifact": source_artifact,
            "source_location": source_location,
            "enriched_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "network_access_performed": False,
    }


def validate_enrichment_result(
    result: Dict[str, Any],
) -> bool:
    """
    Validate the basic structure of a unified enrichment result.
    """

    required_fields = {
        "enrichment_id",
        "ioc_type",
        "value",
        "enrichment",
        "provenance",
        "network_access_performed",
    }

    if not required_fields.issubset(result.keys()):
        return False

    if result["ioc_type"] not in SUPPORTED_IOC_TYPES:
        return False

    if not isinstance(result["value"], str):
        return False

    if not isinstance(result["enrichment"], dict):
        return False

    if not isinstance(result["provenance"], dict):
        return False

    if result["network_access_performed"] is not False:
        return False

    return True
"""
TRACEWEAVE - Phase 17.2
Forensic Timestamp Extraction
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


SUPPORTED_TIMESTAMP_SOURCES = {
    "EMAIL_HEADER",
    "ICS_PROPERTY",
    "ARTIFACT_METADATA",
    "QR_EXTRACTION",
    "IOC_OBSERVATION",
    "DNS_EVIDENCE",
    "TLS_EVIDENCE",
}


def normalize_timestamp(
    timestamp: str,
) -> str:

    if not isinstance(
        timestamp,
        str,
    ) or not timestamp.strip():

        raise ValueError(
            "Timestamp must be a non-empty string."
        )

    timestamp = timestamp.strip()

    # Support the common trailing Z notation.
    normalized = timestamp.replace(
        "Z",
        "+00:00",
    )

    try:
        parsed = datetime.fromisoformat(
            normalized
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid timestamp: {timestamp}"
        ) from exc

    # If evidence contains no timezone,
    # preserve the timestamp but explicitly
    # treat it as timezone-unknown.
    if parsed.tzinfo is None:
        return parsed.isoformat()

    return parsed.astimezone(
        timezone.utc
    ).isoformat()


def create_timestamp_observation(
    timestamp: str,
    source_type: str,
    source_artifact: str,
    source_location: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:

    source_type = source_type.upper()

    if source_type not in (
        SUPPORTED_TIMESTAMP_SOURCES
    ):
        raise ValueError(
            f"Unsupported timestamp source: "
            f"{source_type}"
        )

    if not source_artifact:
        raise ValueError(
            "source_artifact cannot be empty."
        )

    if not source_location:
        raise ValueError(
            "source_location cannot be empty."
        )

    if not isinstance(
        evidence,
        dict,
    ):
        raise ValueError(
            "evidence must be a dictionary."
        )

    normalized_timestamp = normalize_timestamp(
        timestamp
    )

    return {
        "timestamp": normalized_timestamp,
        "source_type": source_type,
        "source_artifact": source_artifact,
        "source_location": source_location,
        "evidence": evidence,
        "temporal_status": "OBSERVED",
    }


def extract_email_timestamp(
    email_data: Dict[str, Any],
    source_artifact: str,
) -> Optional[Dict[str, Any]]:

    headers = email_data.get(
        "headers",
        {}
    )

    if not isinstance(
        headers,
        dict,
    ):
        return None

    date_value = headers.get(
        "date"
    )

    if not date_value:
        return None

    return create_timestamp_observation(
        timestamp=date_value,
        source_type="EMAIL_HEADER",
        source_artifact=source_artifact,
        source_location="Date",
        evidence={
            "method": "EMAIL_HEADER_EXTRACTION",
            "header": "Date",
        },
    )


def extract_ics_timestamps(
    ics_data: Dict[str, Any],
    source_artifact: str,
) -> List[Dict[str, Any]]:

    observations = []

    components = ics_data.get(
        "components",
        []
    )

    if not isinstance(
        components,
        list,
    ):
        return observations

    for index, component in enumerate(
        components
    ):

        if not isinstance(
            component,
            dict,
        ):
            continue

        component_type = component.get(
            "component"
        )

        for property_name in (
            "DTSTART",
            "DTEND",
            "DTSTAMP",
            "CREATED",
            "LAST-MODIFIED",
        ):

            value = component.get(
                property_name
            )

            if not value:
                continue

            if isinstance(
                value,
                dict,
            ):
                value = value.get(
                    "value"
                )

            if value is None:
                continue

            observations.append(
                create_timestamp_observation(
                    timestamp=str(value),
                    source_type="ICS_PROPERTY",
                    source_artifact=source_artifact,
                    source_location=(
                        f"{component_type}"
                        f"[{index}]."
                        f"{property_name}"
                    ),
                    evidence={
                        "method":
                            "ICS_PROPERTY_EXTRACTION",
                        "property":
                            property_name,
                        "component":
                            component_type,
                    },
                )
            )

    return observations


def validate_timestamp_observation(
    observation: Dict[str, Any],
) -> None:

    required_fields = {
        "timestamp",
        "source_type",
        "source_artifact",
        "source_location",
        "evidence",
        "temporal_status",
    }

    missing = (
        required_fields
        - set(observation.keys())
    )

    if missing:
        raise ValueError(
            "Timestamp observation missing "
            f"fields: {sorted(missing)}"
        )

    if observation[
        "source_type"
    ] not in SUPPORTED_TIMESTAMP_SOURCES:

        raise ValueError(
            "Unsupported timestamp source."
        )

    normalize_timestamp(
        observation["timestamp"]
    )

    if observation[
        "temporal_status"
    ] != "OBSERVED":

        raise ValueError(
            "Timestamp observation must "
            "remain OBSERVED."
        )
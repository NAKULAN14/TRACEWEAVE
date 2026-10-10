"""
TRACEWEAVE - Phase 16.3
Incident Object Model
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


SUPPORTED_INCIDENT_STATUSES = {
    "OPEN",
    "UNDER_INVESTIGATION",
    "RECONSTRUCTED",
    "CLOSED",
}


def create_incident(
    case_id: str,
    title: str,
) -> Dict[str, Any]:

    if not isinstance(
        case_id,
        str,
    ) or not case_id.strip():

        raise ValueError(
            "case_id must be a non-empty string."
        )

    if not isinstance(
        title,
        str,
    ) or not title.strip():

        raise ValueError(
            "title must be a non-empty string."
        )

    case_id = case_id.strip()
    title = title.strip()

    return {
        "incident_id": f"INC-{case_id}",
        "case_id": case_id,
        "title": title,
        "status": "OPEN",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "artifacts": [],
        "evidence_links": [],
        "iocs": [],
        "infrastructure_graph": None,
        "timeline_events": [],
        "attack_stages": [],
        "findings": [],
    }


def add_artifact(
    incident: Dict[str, Any],
    artifact: Dict[str, Any],
) -> None:

    if not isinstance(
        artifact,
        dict,
    ):
        raise ValueError(
            "Artifact must be a dictionary."
        )

    artifact_id = artifact.get(
        "artifact_id"
    )

    if not artifact_id:
        raise ValueError(
            "Artifact must contain artifact_id."
        )

    existing_ids = {
        item.get("artifact_id")
        for item in incident[
            "artifacts"
        ]
    }

    if artifact_id not in existing_ids:
        incident[
            "artifacts"
        ].append(artifact)

    _touch_incident(incident)


def add_evidence_link(
    incident: Dict[str, Any],
    link: Dict[str, Any],
) -> None:

    if not isinstance(
        link,
        dict,
    ):
        raise ValueError(
            "Evidence link must be a dictionary."
        )

    link_id = link.get(
        "link_id"
    )

    if not link_id:
        raise ValueError(
            "Evidence link must contain link_id."
        )

    existing_ids = {
        item.get("link_id")
        for item in incident[
            "evidence_links"
        ]
    }

    if link_id not in existing_ids:
        incident[
            "evidence_links"
        ].append(link)

    _touch_incident(incident)


def add_ioc(
    incident: Dict[str, Any],
    ioc: Dict[str, Any],
) -> None:

    if not isinstance(
        ioc,
        dict,
    ):
        raise ValueError(
            "IOC must be a dictionary."
        )

    ioc_key = (
        ioc.get("ioc_type"),
        ioc.get("canonical_value"),
    )

    existing_keys = {
        (
            item.get("ioc_type"),
            item.get("canonical_value"),
        )
        for item in incident[
            "iocs"
        ]
    }

    if ioc_key not in existing_keys:
        incident[
            "iocs"
        ].append(ioc)

    _touch_incident(incident)


def attach_infrastructure_graph(
    incident: Dict[str, Any],
    graph: Dict[str, Any],
) -> None:

    if not isinstance(
        graph,
        dict,
    ):
        raise ValueError(
            "Infrastructure graph must be a dictionary."
        )

    incident[
        "infrastructure_graph"
    ] = graph

    _touch_incident(incident)


def set_status(
    incident: Dict[str, Any],
    status: str,
) -> None:

    status = status.upper()

    if status not in (
        SUPPORTED_INCIDENT_STATUSES
    ):
        raise ValueError(
            f"Unsupported incident status: {status}"
        )

    incident[
        "status"
    ] = status

    _touch_incident(incident)


def _touch_incident(
    incident: Dict[str, Any],
) -> None:

    incident[
        "updated_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


def validate_incident(
    incident: Dict[str, Any],
) -> None:

    required_fields = {
        "incident_id",
        "case_id",
        "title",
        "status",
        "created_at",
        "updated_at",
        "artifacts",
        "evidence_links",
        "iocs",
        "infrastructure_graph",
        "timeline_events",
        "attack_stages",
        "findings",
    }

    missing = (
        required_fields
        - set(incident.keys())
    )

    if missing:
        raise ValueError(
            "Incident object missing fields: "
            f"{sorted(missing)}"
        )

    if incident[
        "status"
    ] not in SUPPORTED_INCIDENT_STATUSES:

        raise ValueError(
            f"Invalid incident status: "
            f"{incident['status']}"
        )

    list_fields = [
        "artifacts",
        "evidence_links",
        "iocs",
        "timeline_events",
        "attack_stages",
        "findings",
    ]

    for field in list_fields:

        if not isinstance(
            incident[field],
            list,
        ):
            raise ValueError(
                f"Incident field '{field}' "
                f"must be a list."
            )

    artifact_ids = [
        artifact.get(
            "artifact_id"
        )
        for artifact in incident[
            "artifacts"
        ]
    ]

    if len(artifact_ids) != len(
        set(artifact_ids)
    ):
        raise ValueError(
            "Incident contains duplicate artifacts."
        )

    link_ids = [
        link.get("link_id")
        for link in incident[
            "evidence_links"
        ]
    ]

    if len(link_ids) != len(
        set(link_ids)
    ):
        raise ValueError(
            "Incident contains duplicate evidence links."
        )
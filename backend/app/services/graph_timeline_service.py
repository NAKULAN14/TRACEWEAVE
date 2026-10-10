
from backend.app.models.investigation import Investigation


def get_investigation(db, investigation_id: str):
    return (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id == investigation_id
        )
        .first()
    )


def get_infrastructure_graph(db, investigation_id: str):
    investigation = get_investigation(db, investigation_id)

    if investigation is None:
        return None

    # Actual graph output will be connected in a later integration step.
    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "status": "NOT_AVAILABLE",
        "nodes": [],
        "relationships": [],
        "message": (
            "Infrastructure graph has not been connected "
            "to the investigation execution pipeline yet."
        ),
    }


def get_investigation_timeline(db, investigation_id: str):
    investigation = get_investigation(db, investigation_id)

    if investigation is None:
        return None

    # Actual timeline output will be connected in a later integration step.
    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "status": "NOT_AVAILABLE",
        "events": [],
        "message": (
            "Timeline output has not been connected "
            "to the investigation execution pipeline yet."
        ),
    }

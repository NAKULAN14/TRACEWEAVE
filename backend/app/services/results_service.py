
from backend.app.models.investigation import Investigation


SUPPORTED_RESULT_TYPES = {
    "iocs",
    "infrastructure",
    "timeline",
    "attack-chain",
    "risk",
    "recommendations",
}


def get_investigation_result(db, investigation_id: str, result_type: str):
    investigation = (
        db.query(Investigation)
        .filter(Investigation.investigation_id == investigation_id)
        .first()
    )

    if investigation is None:
        return None

    if result_type not in SUPPORTED_RESULT_TYPES:
        raise ValueError(f"Unsupported result type: {result_type}")

    # The analysis pipeline is not connected yet.
    # point to be noted
    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "result_type": result_type,
        "status": "NOT_AVAILABLE",
        "data": None,
        "message": (
            "Results are not available yet. "
            "The forensic analysis pipeline has not been connected."
        ),
    }

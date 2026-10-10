
from backend.app.models.investigation import Investigation


def _get_investigation(db, investigation_id: str):
    return (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id == investigation_id
        )
        .first()
    )


def get_risk_assessment(db, investigation_id: str):
    investigation = _get_investigation(db, investigation_id)

    if investigation is None:
        return None

    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "status": "NOT_AVAILABLE",
        "overall_risk": None,
        "risk_score": None,
        "factors": [],
        "message": (
            "Risk assessment output has not been connected "
            "to the investigation execution pipeline yet."
        ),
    }


def get_recommendations(db, investigation_id: str):
    investigation = _get_investigation(db, investigation_id)

    if investigation is None:
        return None

    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "status": "NOT_AVAILABLE",
        "recommendations": [],
        "message": (
            "Recommendation output has not been connected "
            "to the investigation execution pipeline yet."
        ),
    }

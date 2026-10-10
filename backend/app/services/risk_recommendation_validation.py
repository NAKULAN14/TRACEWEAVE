
from backend.app.database import SessionLocal
from backend.app.models.investigation import Investigation
from backend.app.services.risk_recommendation_service import (
    get_risk_assessment,
    get_recommendations,
)


def validate_risk_recommendations():
    db = SessionLocal()

    try:
        investigation = db.query(Investigation).first()

        if investigation is None:
            raise ValueError(
                "No investigations found. Create an investigation first."
            )

        risk = get_risk_assessment(
            db, investigation.investigation_id
        )
        recommendations = get_recommendations(
            db, investigation.investigation_id
        )

        if risk is None or recommendations is None:
            raise AssertionError("Could not retrieve API results.")

        if risk["case_id"] != investigation.case_id:
            raise AssertionError("Risk assessment case ID mismatch.")

        if recommendations["case_id"] != investigation.case_id:
            raise AssertionError("Recommendations case ID mismatch.")

        if risk["status"] != "NOT_AVAILABLE":
            raise AssertionError("Unexpected risk status.")

        if recommendations["status"] != "NOT_AVAILABLE":
            raise AssertionError("Unexpected recommendations status.")

        if not isinstance(risk["factors"], list):
            raise AssertionError("Risk factors must be a list.")

        if not isinstance(recommendations["recommendations"], list):
            raise AssertionError("Recommendations must be a list.")

        if get_risk_assessment(db, "INV-DOES-NOT-EXIST") is not None:
            raise AssertionError("Unknown risk investigation should return None.")

        if get_recommendations(db, "INV-DOES-NOT-EXIST") is not None:
            raise AssertionError("Unknown recommendation investigation should return None.")

        print("RISK AND RECOMMENDATIONS VALIDATION: PASS")
        print("Risk assessment: PASS")
        print("Recommendations: PASS")
        print("Unknown investigation handling: PASS")

    finally:
        db.close()


if __name__ == "__main__":
    validate_risk_recommendations()

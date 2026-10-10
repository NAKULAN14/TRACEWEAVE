
from backend.app.database import SessionLocal
from backend.app.models.investigation import Investigation
from backend.app.services.results_service import (
    SUPPORTED_RESULT_TYPES,
    get_investigation_result,
)


def validate_results_service():
    db = SessionLocal()

    try:
        investigation = db.query(Investigation).first()

        if investigation is None:
            raise ValueError(
                "No investigations found. Create an investigation first."
            )

        if not SUPPORTED_RESULT_TYPES:
            raise ValueError("No result types registered.")

        checked = 0

        for result_type in sorted(SUPPORTED_RESULT_TYPES):
            result = get_investigation_result(
                db,
                investigation.investigation_id,
                result_type,
            )

            if result is None:
                raise AssertionError(
                    f"Result lookup failed for {result_type}."
                )

            if result["investigation_id"] != investigation.investigation_id:
                raise AssertionError("Investigation ID mismatch.")

            if result["case_id"] != investigation.case_id:
                raise AssertionError("Case ID mismatch.")

            if result["result_type"] != result_type:
                raise AssertionError("Result type mismatch.")

            if result["status"] != "NOT_AVAILABLE":
                raise AssertionError("Unexpected result status.")

            checked += 1

        if get_investigation_result(
            db, "INV-DOES-NOT-EXIST", "iocs"
        ) is not None:
            raise AssertionError(
                "Unknown investigation should return None."
            )

        print("RESULTS SERVICE VALIDATION: PASS")
        print("Result types checked:", checked)

        return checked

    finally:
        db.close()


if __name__ == "__main__":
    validate_results_service()

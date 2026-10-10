
from backend.app.database import SessionLocal
from backend.app.models.investigation import Investigation
from backend.app.services.report_service import get_investigation_report


def validate_report_service():
    db = SessionLocal()

    try:
        investigation = db.query(Investigation).first()

        if investigation is None:
            raise ValueError(
                "No investigations found. Create an investigation first."
            )

        for report_format in ("json", "html", "markdown"):
            report = get_investigation_report(
                db,
                investigation.investigation_id,
                report_format,
            )

            if report is None:
                raise AssertionError("Report lookup failed.")

            if report["case_id"] != investigation.case_id:
                raise AssertionError("Report case ID mismatch.")

            if report["status"] != "NOT_AVAILABLE":
                raise AssertionError("Unexpected report status.")

            if report["report_format"] != report_format:
                raise AssertionError("Report format mismatch.")

            if report["report_content"] is not None:
                raise AssertionError(
                    "Unavailable report must not contain fabricated content."
                )

        if get_investigation_report(
            db, "INV-DOES-NOT-EXIST", "json"
        ) is not None:
            raise AssertionError(
                "Unknown investigation should return None."
            )

        try:
            get_investigation_report(
                db, investigation.investigation_id, "pdf"
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Unsupported report format was accepted.")

        print("REPORT SERVICE VALIDATION: PASS")
        print("Formats checked: JSON, HTML, Markdown")
        print("Unknown investigation handling: PASS")
        print("Unsupported format handling: PASS")

    finally:
        db.close()


if __name__ == "__main__":
    validate_report_service()

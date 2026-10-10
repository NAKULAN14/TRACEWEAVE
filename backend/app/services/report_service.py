
from backend.app.models.investigation import Investigation


def get_investigation_report(
    db,
    investigation_id: str,
    report_format: str = "json",
):
    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id == investigation_id
        )
        .first()
    )

    if investigation is None:
        return None

    report_format = report_format.lower()

    if report_format not in {"json", "html", "markdown"}:
        raise ValueError(
            "Unsupported report format. Use json, html, or markdown."
        )

    return {
        "investigation_id": investigation.investigation_id,
        "case_id": investigation.case_id,
        "status": "NOT_AVAILABLE",
        "report_format": report_format,
        "report_content": None,
        "message": (
            "The investigation report has not been generated yet. "
            "Report generation will be connected to the forensic "
            "pipeline in a later integration step."
        ),
    }

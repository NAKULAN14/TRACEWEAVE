"""
TRACEWEAVE - Investigation Validation
"""

from backend.app.database import SessionLocal
from backend.app.models.case import Case
from backend.app.models.investigation import Investigation
from backend.app.services.investigation_service import (
    validate_investigation,
)
from backend.app.services.investigation_status import (
    build_stage_status,
)


def validate_all_investigations():
    db = SessionLocal()

    try:
        investigations = (
            db.query(Investigation).all()
        )

        if not investigations:
            raise ValueError(
                "No investigations found. "
                "Create an investigation first."
            )

        seen_ids = set()

        for investigation in investigations:

            # 1. Validate investigation lifecycle
            validate_investigation(
                investigation
            )

            # 2. Check unique IDs
            if investigation.investigation_id in seen_ids:
                raise ValueError(
                    "Duplicate investigation ID."
                )

            seen_ids.add(
                investigation.investigation_id
            )

            # 3. Confirm parent case exists
            case = (
                db.query(Case)
                .filter(
                    Case.case_id
                    == investigation.case_id
                )
                .first()
            )

            if case is None:
                raise ValueError(
                    f"Investigation "
                    f"{investigation.investigation_id} "
                    "references a missing case."
                )

            # 4. Validate stage-status output
            stages = build_stage_status(
                investigation
            )

            if len(stages) == 0:
                raise ValueError(
                    "Investigation has no stages."
                )

            sequences = [
                stage["sequence"]
                for stage in stages
            ]

            expected = list(
                range(1, len(stages) + 1)
            )

            if sequences != expected:
                raise ValueError(
                    "Stage sequence is invalid."
                )

            # 5. Check terminal states
            if investigation.status in (
                "COMPLETED",
                "FAILED",
            ):
                if investigation.completed_at is None:
                    raise ValueError(
                        "Terminal investigation "
                        "is missing completed_at."
                    )

            if investigation.status == "FAILED":
                if not investigation.error_message:
                    raise ValueError(
                        "Failed investigation is "
                        "missing its error message."
                    )

        return {
            "investigation_count": len(
                investigations
            ),
            "validated_count": len(
                seen_ids
            ),
        }

    finally:
        db.close()


if __name__ == "__main__":

    result = validate_all_investigations()

    print(
        "INVESTIGATION VALIDATION: PASS"
    )
    print(
        "Investigations:",
        result["investigation_count"],
    )
    print(
        "Validated:",
        result["validated_count"],
    )
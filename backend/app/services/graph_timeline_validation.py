
from backend.app.database import SessionLocal
from backend.app.models.investigation import Investigation
from backend.app.services.graph_timeline_service import (
    get_infrastructure_graph,
    get_investigation_timeline,
)


def validate_graph_timeline():
    db = SessionLocal()

    try:
        investigation = db.query(Investigation).first()

        if investigation is None:
            raise ValueError(
                "No investigations found. Create an investigation first."
            )

        graph = get_infrastructure_graph(
            db, investigation.investigation_id
        )
        timeline = get_investigation_timeline(
            db, investigation.investigation_id
        )

        if graph is None or timeline is None:
            raise AssertionError("Could not retrieve investigation outputs.")

        if graph["case_id"] != investigation.case_id:
            raise AssertionError("Graph case ID mismatch.")

        if timeline["case_id"] != investigation.case_id:
            raise AssertionError("Timeline case ID mismatch.")

        if not isinstance(graph["nodes"], list):
            raise AssertionError("Graph nodes must be a list.")

        if not isinstance(graph["relationships"], list):
            raise AssertionError("Graph relationships must be a list.")

        if not isinstance(timeline["events"], list):
            raise AssertionError("Timeline events must be a list.")

        if graph["status"] != "NOT_AVAILABLE":
            raise AssertionError("Unexpected graph status.")

        if timeline["status"] != "NOT_AVAILABLE":
            raise AssertionError("Unexpected timeline status.")

        if get_infrastructure_graph(db, "INV-DOES-NOT-EXIST") is not None:
            raise AssertionError("Unknown graph investigation should return None.")

        if get_investigation_timeline(db, "INV-DOES-NOT-EXIST") is not None:
            raise AssertionError("Unknown timeline investigation should return None.")

        print("GRAPH AND TIMELINE VALIDATION: PASS")
        print("Infrastructure graph: PASS")
        print("Timeline: PASS")
        print("Unknown investigation handling: PASS")

    finally:
        db.close()


if __name__ == "__main__":
    validate_graph_timeline()

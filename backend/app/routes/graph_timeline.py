
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.graph import InfrastructureGraphResponse
from backend.app.schemas.timeline import TimelineResponse
from backend.app.services.graph_timeline_service import (
    get_infrastructure_graph,
    get_investigation_timeline,
)


router = APIRouter(
    prefix="/api/investigations",
    tags=["Graph and Timeline"],
)


@router.get(
    "/{investigation_id}/graph",
    response_model=InfrastructureGraphResponse,
)
def read_infrastructure_graph(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    result = get_infrastructure_graph(db, investigation_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result


@router.get(
    "/{investigation_id}/timeline",
    response_model=TimelineResponse,
)
def read_investigation_timeline(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    result = get_investigation_timeline(db, investigation_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import Base, engine

# Import models before create_all so SQLAlchemy registers their tables.
from backend.app.models.case import Case
from backend.app.models.evidence import Evidence
from backend.app.models.investigation import Investigation

# Import API routers.
from backend.app.routes.cases import router as cases_router
from backend.app.routes.evidence import router as evidence_router
from backend.app.routes.investigations import router as investigations_router
from backend.app.routes.results import router as results_router
from backend.app.routes.graph_timeline import router as graph_timeline_router
from backend.app.routes.risk_recommendations import (
    router as risk_recommendations_router,
)
from backend.app.routes.reports import router as reports_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TRACEWEAVE API",
    description="Forensic reconstruction platform for QR-mediated phishing incidents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers.
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(investigations_router)
app.include_router(results_router)
app.include_router(graph_timeline_router)
app.include_router(risk_recommendations_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "TRACEWEAVE API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

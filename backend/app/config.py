"""
TRACEWEAVE Backend Configuration
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKEND_ROOT = PROJECT_ROOT / "backend"

DATASET_ROOT = PROJECT_ROOT / "dataset"

REPORTS_ROOT = PROJECT_ROOT / "reports"

STORAGE_ROOT = BACKEND_ROOT / "storage"

EVIDENCE_ROOT = STORAGE_ROOT / "evidence"

DATABASE_PATH = STORAGE_ROOT / "traceweave.db"

DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH}"
)


# Create required directories.
STORAGE_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

EVIDENCE_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

REPORTS_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)
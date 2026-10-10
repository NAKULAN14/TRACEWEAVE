import csv
import json
from pathlib import Path

# Change this only if your Traceweave folder is somewhere else
DATASET_ROOT = Path("dataset")
OUTPUT_FILE = DATASET_ROOT / "dataset_manifest.csv"


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


rows = []

# ---------------------------------------------------------
# Dataset 1: Benign Email + ICS
# ---------------------------------------------------------
base = DATASET_ROOT / "benign_email_ics" / "cases"

if base.exists():
    for case_dir in sorted(base.iterdir()):
        if not case_dir.is_dir():
            continue

        case_id = case_dir.name
        gt_file = case_dir / "ground_truth.json"
        gt = read_json(gt_file)

        rows.append({
            "case_id": case_id,
            "dataset": "benign_email_ics",
            "category": "benign",
            "artifacts": ";".join(
                p.name for p in case_dir.iterdir() if p.is_file()
            ),
            "ground_truth": gt_file.name if gt_file.exists() else "",
            "classification": gt.get("category", "benign"),
            "path": str(case_dir)
        })


# ---------------------------------------------------------
# Dataset 2: Benign QR
# ---------------------------------------------------------
base = DATASET_ROOT / "benign_qr" / "cases"

if base.exists():
    for case_dir in sorted(base.iterdir()):
        if not case_dir.is_dir():
            continue

        case_id = case_dir.name
        gt_file = case_dir / "ground_truth.json"
        gt = read_json(gt_file)

        rows.append({
            "case_id": case_id,
            "dataset": "benign_qr",
            "category": "benign",
            "artifacts": ";".join(
                p.name for p in case_dir.iterdir() if p.is_file()
            ),
            "ground_truth": gt_file.name if gt_file.exists() else "",
            "classification": gt.get("category", "benign"),
            "path": str(case_dir)
        })


# ---------------------------------------------------------
# Dataset 3: Malformed ICS
# ---------------------------------------------------------
base = DATASET_ROOT / "malformed_ics"

originals = base / "originals"
corrupted = base / "corrupted"
ground_truth = base / "ground_truth"

if ground_truth.exists():
    for gt_file in sorted(ground_truth.glob("*.json")):

        gt = read_json(gt_file)
        case_id = gt.get("case_id", gt_file.stem)

        original_file = originals / gt_file.name.replace(".json", ".ics")
        corrupted_file = corrupted / gt_file.name.replace(".json", ".ics")

        artifacts = []

        if original_file.exists():
            artifacts.append(original_file.name)

        if corrupted_file.exists():
            artifacts.append(corrupted_file.name)

        rows.append({
            "case_id": case_id,
            "dataset": "malformed_ics",
            "category": "malformed_ics",
            "artifacts": ";".join(artifacts),
            "ground_truth": gt_file.name,
            "classification": "malformed_ics",
            "path": str(base)
        })


# ---------------------------------------------------------
# Dataset 4: QR Phishing Simulations
# ---------------------------------------------------------
base = DATASET_ROOT / "qr_phishing_simulations" / "cases"

if base.exists():
    for case_dir in sorted(base.iterdir()):
        if not case_dir.is_dir():
            continue

        case_id = case_dir.name
        gt_file = case_dir / "ground_truth.json"
        gt = read_json(gt_file)

        rows.append({
            "case_id": case_id,
            "dataset": "qr_phishing_simulations",
            "category": "qr_phishing_simulation",
            "artifacts": ";".join(
                p.name for p in case_dir.iterdir() if p.is_file()
            ),
            "ground_truth": gt_file.name if gt_file.exists() else "",
            "classification": gt.get(
                "expected_classification",
                "simulated_phishing"
            ),
            "path": str(case_dir)
        })


# ---------------------------------------------------------
# Dataset 5: Combined Complex
# ---------------------------------------------------------
base = DATASET_ROOT / "combined_complex" / "cases"

if base.exists():
    for case_dir in sorted(base.iterdir()):
        if not case_dir.is_dir():
            continue

        case_id = case_dir.name
        gt_file = case_dir / "ground_truth.json"
        gt = read_json(gt_file)

        rows.append({
            "case_id": case_id,
            "dataset": "combined_complex",
            "category": "combined_complex",
            "artifacts": ";".join(
                p.name for p in case_dir.iterdir() if p.is_file()
            ),
            "ground_truth": gt_file.name if gt_file.exists() else "",
            "classification": gt.get(
                "expected_classification",
                "unknown"
            ),
            "path": str(case_dir)
        })


# ---------------------------------------------------------
# Write CSV
# ---------------------------------------------------------

fieldnames = [
    "case_id",
    "dataset",
    "category",
    "artifacts",
    "ground_truth",
    "classification",
    "path"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(rows)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\n========================================")
print(" TRACEWEAVE DATASET MANIFEST")
print("========================================")

print(f"\nTotal cases found: {len(rows)}")

datasets = {}

for row in rows:
    datasets[row["dataset"]] = datasets.get(row["dataset"], 0) + 1

for dataset, count in datasets.items():
    print(f"{dataset}: {count}")

print(f"\nManifest created:")
print(OUTPUT_FILE.resolve())

print("\n========================================")
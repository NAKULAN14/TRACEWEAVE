from pathlib import Path
import argparse
import json
from collections import defaultdict


def build_identity_key(ioc):
    """
    Build a canonical identity key for an IOC.
    """

    ioc_type = ioc.get("type")
    value = ioc.get("value")

    if not ioc_type or not value:
        return None

    return (
        ioc_type.upper(),
        value.strip().lower()
    )


def deduplicate_records(records):
    """
    Group IOC observations by canonical identity.

    Observations are preserved.
    Only IOC identity is deduplicated.
    """

    groups = defaultdict(list)

    for record in records:

        ioc = record.get("ioc", {})

        identity_key = build_identity_key(
            ioc
        )

        if identity_key is None:
            continue

        groups[identity_key].append(
            record
        )

    unique_iocs = []

    for identity_key, observations in groups.items():

        ioc_type, value = identity_key

        first_ioc = observations[0].get(
            "ioc",
            {}
        )

        unique_iocs.append({
            "ioc_type": ioc_type,

            "canonical_value": value,

            "observation_count": len(
                observations
            ),

            "original_values": sorted(
                set(
                    observation.get(
                        "ioc",
                        {}
                    ).get(
                        "original_value"
                    )
                    for observation in observations
                    if observation.get(
                        "ioc",
                        {}
                    ).get(
                        "original_value"
                    )
                )
            ),

            "observations": observations,

            "first_ioc_id": first_ioc.get(
                "ioc_id"
            ),
        })

    return unique_iocs


def build_summary(
    unique_iocs,
    total_observations
):

    type_counts = defaultdict(int)

    duplicate_groups = 0

    for ioc in unique_iocs:

        ioc_type = ioc["ioc_type"]

        type_counts[ioc_type] += 1

        if ioc["observation_count"] > 1:
            duplicate_groups += 1

    unique_count = len(
        unique_iocs
    )

    duplicates_removed = (
        total_observations - unique_count
    )

    return {
        "total_observations": total_observations,

        "unique_iocs": unique_count,

        "duplicate_observations": (
            duplicates_removed
        ),

        "duplicate_groups": (
            duplicate_groups
        ),

        "unique_ioc_type_counts": dict(
            type_counts
        ),
    }


def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE IOC Deduplication Engine"
        )
    )

    parser.add_argument(
        "input_file",
        help="ioc_records.json"
    )

    parser.add_argument(
        "--output",
        default="reports/phase12/deduplicated_iocs.json"
    )

    args = parser.parse_args()

    input_path = Path(
        args.input_file
    )

    output_path = Path(
        args.output
    )

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        records = json.load(f)

    unique_iocs = deduplicate_records(
        records
    )

    summary = build_summary(
        unique_iocs,
        len(records)
    )

    result = {
        "summary": summary,
        "iocs": unique_iocs,
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    print(
        "\n=== TRACEWEAVE IOC DEDUPLICATION ==="
    )

    print(
        f"Total observations : "
        f"{summary['total_observations']}"
    )

    print(
        f"Unique IOCs        : "
        f"{summary['unique_iocs']}"
    )

    print(
        f"Duplicate observations removed: "
        f"{summary['duplicate_observations']}"
    )

    print(
        f"Duplicate groups   : "
        f"{summary['duplicate_groups']}"
    )

    print(
        f"\nSaved to: {output_path}"
    )


if __name__ == "__main__":
    main()
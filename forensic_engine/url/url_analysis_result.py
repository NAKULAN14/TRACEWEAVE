from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def build_url_analysis_result(
    source_artifact,
    original_url,
    normalization_result,
    parsing_result,
    indicator_result
):
    """
    Build a provenance-preserving URL analysis record.
    """

    artifact_path = Path(source_artifact)

    normalized_url = normalization_result.get(
        "normalized_url"
    )

    result = {
        "artifact": {
            "filename": artifact_path.name,
            "path": str(artifact_path),
            "sha256": calculate_sha256(artifact_path),
        },

        "analysis": {
            "analyzed_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "status": "SUCCESS"
        },

        "source": {
            "original_url": original_url,
            "source_type": "QR_PAYLOAD"
        },

        "normalization": {
            "normalized_url": normalized_url,
            "changed": normalization_result.get(
                "normalization_changed",
                False
            )
        },

        "structure": parsing_result,

        "indicators": {
            "count": indicator_result.get(
                "indicator_count",
                0
            ),
            "items": indicator_result.get(
                "indicators",
                []
            )
        },

        "provenance": {
            "original_artifact_preserved": True,
            "source_artifact": artifact_path.name,
            "analysis_engine": (
                "TRACEWEAVE URL Analysis Engine"
            ),
            "network_access_performed": False
        }
    }

    return result


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE URL Analysis Result Builder"
    )

    parser.add_argument(
        "artifact",
        help="Source artifact containing the URL"
    )

    parser.add_argument(
        "url",
        help="Original extracted URL"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path"
    )

    args = parser.parse_args()

    try:

        from forensic_engine.url.url_normalizer import (
            normalize_url
        )

        from forensic_engine.url.url_parser import (
            parse_url
        )

        from forensic_engine.url.url_indicators import (
            analyze_url_indicators
        )

        normalization_result = normalize_url(
            args.url
        )

        normalized_url = normalization_result[
            "normalized_url"
        ]

        parsing_result = parse_url(
            normalized_url
        )

        indicator_result = analyze_url_indicators(
            normalized_url
        )

        result = build_url_analysis_result(
            args.artifact,
            args.url,
            normalization_result,
            parsing_result,
            indicator_result
        )

        print(
            json.dumps(
                result,
                indent=2
            )
        )

        if args.output:

            output_path = Path(args.output)

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
                f"\nSaved result to: {output_path}"
            )

    except Exception as exc:

        print(
            json.dumps(
                {
                    "status": "FAILED",
                    "error": str(exc)
                },
                indent=2
            )
        )


if __name__ == "__main__":
    main()
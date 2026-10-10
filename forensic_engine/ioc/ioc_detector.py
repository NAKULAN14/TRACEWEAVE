import argparse
import json
import re


PATTERNS = {

    "URL": re.compile(
        r"https?://[^\s<>'\"\\]+",
        re.IGNORECASE
    ),

    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "IPV4": re.compile(
        r"\b"
        r"(?:"
        r"(?:25[0-5]|2[0-4]\d|1\d\d|"
        r"[1-9]?\d)"
        r"\."
        r"){3}"
        r"(?:25[0-5]|2[0-4]\d|1\d\d|"
        r"[1-9]?\d)"
        r"\b"
    ),

    "SHA256": re.compile(
        r"\b[a-fA-F0-9]{64}\b"
    ),

    "SHA1": re.compile(
        r"\b[a-fA-F0-9]{40}\b"
    ),

    "MD5": re.compile(
        r"\b[a-fA-F0-9]{32}\b"
    ),

    "DOMAIN": re.compile(
        r"\b"
        r"(?:[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}"
        r"[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,}"
        r"\b"
    ),
}


def detect_iocs(text):
    """
    Detect potential IOCs from arbitrary text.

    This function performs pattern detection only.
    It does not determine whether an IOC is malicious.
    """

    if not text:
        return []

    observations = []

    for ioc_type, pattern in PATTERNS.items():

        matches = pattern.findall(text)

        for value in matches:

            observations.append({
                "type": ioc_type,
                "value": value,
            })

    return observations


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE IOC Detector"
    )

    parser.add_argument(
        "text",
        help="Text to scan for IOCs"
    )

    args = parser.parse_args()

    try:

        observations = detect_iocs(
            args.text
        )

        result = {
            "status": "SUCCESS",
            "ioc_count": len(observations),
            "iocs": observations,
        }

    except Exception as exc:

        result = {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        json.dumps(
            result,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
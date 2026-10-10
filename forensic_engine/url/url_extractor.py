from pathlib import Path
import argparse
import json
import re


URL_PATTERN = re.compile(
    r"https?://[^\s<>'\"\\]+",
    re.IGNORECASE
)


def extract_urls(text):
    """
    Extract HTTP/HTTPS URLs from arbitrary text.
    """

    if not text:
        return []

    matches = URL_PATTERN.findall(text)

    cleaned_urls = []

    for url in matches:

        # Remove common punctuation that may surround a URL
        url = url.rstrip(
            ".,;:!?)]}"
        )

        if url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def extract_url_records(text):
    """
    Return structured URL extraction records.
    """

    urls = extract_urls(text)

    return [
        {
            "url": url,
            "source": "QR_PAYLOAD",
            "extraction_method": "REGEX_HTTP_HTTPS",
        }
        for url in urls
    ]


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE URL Extractor"
    )

    parser.add_argument(
        "text",
        help="Text containing URLs"
    )

    args = parser.parse_args()

    result = {
        "status": "SUCCESS",
        "url_count": 0,
        "urls": []
    }

    try:

        records = extract_url_records(
            args.text
        )

        result["url_count"] = len(records)
        result["urls"] = records

    except Exception as exc:

        result["status"] = "FAILED"
        result["error"] = str(exc)

    print(
        json.dumps(
            result,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
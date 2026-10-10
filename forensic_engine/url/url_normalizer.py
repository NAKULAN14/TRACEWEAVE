from urllib.parse import urlsplit, urlunsplit
import argparse
import json


def normalize_url(url):
    """
    Normalize an HTTP/HTTPS URL without making any network request.
    """

    if not url:
        raise ValueError("URL cannot be empty")

    original_url = url

    parsed = urlsplit(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(
            "Only HTTP and HTTPS URLs are supported"
        )

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname

    if not hostname:
        raise ValueError(
            "URL does not contain a valid hostname"
        )

    hostname = hostname.lower()

    # Preserve username/password if present.
    userinfo = ""

    if parsed.username is not None:

        userinfo = parsed.username

        if parsed.password is not None:
            userinfo += ":" + parsed.password

        userinfo += "@"

    # Handle port.
    port = parsed.port

    if port is not None:

        is_default_port = (
            (scheme == "http" and port == 80)
            or
            (scheme == "https" and port == 443)
        )

        if not is_default_port:
            hostname = f"{hostname}:{port}"

    netloc = userinfo + hostname

    # Normalize path.
    path = parsed.path

    if not path:
        path = "/"

    elif path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    normalized = urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            parsed.fragment
        )
    )

    return {
        "original_url": original_url,
        "normalized_url": normalized,
        "normalization_changed": (
            original_url != normalized
        )
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE URL Normalizer"
    )

    parser.add_argument(
        "url",
        help="URL to normalize"
    )

    args = parser.parse_args()

    try:

        result = normalize_url(args.url)

        output = {
            "status": "SUCCESS",
            **result
        }

    except Exception as exc:

        output = {
            "status": "FAILED",
            "error": str(exc)
        }

    print(
        json.dumps(
            output,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
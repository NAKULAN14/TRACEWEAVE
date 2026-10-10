from urllib.parse import urlsplit, parse_qsl
import argparse
import json


def parse_url(url):
    """
    Parse a normalized URL into forensic components.
    No network requests are performed.
    """

    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlsplit(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(
            "Only HTTP and HTTPS URLs are supported"
        )

    hostname = parsed.hostname

    if not hostname:
        raise ValueError(
            "URL does not contain a hostname"
        )

    hostname = hostname.lower()

    port = parsed.port

    # Basic registrable-domain approximation.
    # Full public-suffix processing will be handled separately
    # when we build the intelligence layer.
    hostname_parts = hostname.split(".")

    if len(hostname_parts) >= 2:
        domain = ".".join(hostname_parts[-2:])
        subdomain = ".".join(hostname_parts[:-2])
    else:
        domain = hostname
        subdomain = ""

    query_parameters = [
        {
            "key": key,
            "value": value
        }
        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True
        )
    ]

    return {
        "scheme": parsed.scheme.lower(),
        "hostname": hostname,
        "port": port,
        "domain": domain,
        "subdomain": subdomain,
        "path": parsed.path or "/",
        "query": parsed.query,
        "query_parameters": query_parameters,
        "fragment": parsed.fragment,
        "username_present": parsed.username is not None,
        "password_present": parsed.password is not None,
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE URL Structural Parser"
    )

    parser.add_argument(
        "url",
        help="Normalized URL to parse"
    )

    args = parser.parse_args()

    try:

        result = parse_url(args.url)

        output = {
            "status": "SUCCESS",
            "url": args.url,
            "components": result
        }

    except Exception as exc:

        output = {
            "status": "FAILED",
            "url": args.url,
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
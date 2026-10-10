import argparse
import json
import re
from urllib.parse import urlsplit, urlunsplit


def normalize_url(value):
    parsed = urlsplit(value)

    scheme = parsed.scheme.lower()
    hostname = (
        parsed.hostname.lower()
        if parsed.hostname
        else ""
    )

    port = parsed.port

    if port is not None:
        default_port = (
            (scheme == "http" and port == 80)
            or
            (scheme == "https" and port == 443)
        )

        if not default_port:
            hostname = f"{hostname}:{port}"

    path = parsed.path

    if not path:
        path = "/"
    elif path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return urlunsplit(
        (
            scheme,
            hostname,
            path,
            parsed.query,
            parsed.fragment
        )
    )


def normalize_email(value):
    return value.strip().lower()


def normalize_domain(value):
    return value.strip().lower().rstrip(".")


def normalize_ipv4(value):
    return value.strip()


def normalize_hash(value):
    return value.strip().lower()


def normalize_ioc(ioc_type, value):
    """
    Normalize an IOC while preserving its original value.
    """

    if not value:
        raise ValueError(
            "IOC value cannot be empty"
        )

    original_value = value

    if ioc_type == "URL":
        normalized_value = normalize_url(value)

    elif ioc_type == "EMAIL":
        normalized_value = normalize_email(value)

    elif ioc_type == "DOMAIN":
        normalized_value = normalize_domain(value)

    elif ioc_type == "IPV4":
        normalized_value = normalize_ipv4(value)

    elif ioc_type in {
        "MD5",
        "SHA1",
        "SHA256"
    }:
        normalized_value = normalize_hash(value)

    else:
        raise ValueError(
            f"Unsupported IOC type: {ioc_type}"
        )

    return {
        "type": ioc_type,
        "original_value": original_value,
        "normalized_value": normalized_value,
        "changed": (
            original_value != normalized_value
        )
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE IOC Normalizer"
    )

    parser.add_argument(
        "ioc_type",
        choices=[
            "URL",
            "EMAIL",
            "DOMAIN",
            "IPV4",
            "MD5",
            "SHA1",
            "SHA256"
        ]
    )

    parser.add_argument(
        "value",
        help="IOC value"
    )

    args = parser.parse_args()

    try:

        result = normalize_ioc(
            args.ioc_type,
            args.value
        )

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
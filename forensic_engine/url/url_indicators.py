import argparse
import json
import re
from urllib.parse import urlsplit


SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "rb.gy",
    "shorturl.at",
}


SUSPICIOUS_KEYWORDS = {
    "login",
    "verify",
    "verification",
    "account",
    "secure",
    "security",
    "update",
    "password",
    "credential",
    "signin",
    "authenticate",
    "confirm",
    "payment",
    "invoice",
    "wallet",
    "bank",
}


IPV4_PATTERN = re.compile(
    r"^(?:\d{1,3}\.){3}\d{1,3}$"
)


def analyze_url_indicators(url):
    """
    Perform static suspicious-indicator analysis.

    This function does NOT determine whether a URL is malicious.
    """

    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlsplit(url)

    hostname = parsed.hostname or ""
    hostname_lower = hostname.lower()

    indicators = []

    # 1. IP address as hostname
    if IPV4_PATTERN.match(hostname):
        indicators.append({
            "indicator": "IP_ADDRESS_HOST",
            "severity": "MEDIUM",
            "description": "URL uses an IPv4 address instead of a hostname."
        })

    # 2. Embedded credentials / @ symbol
    if parsed.username is not None or parsed.password is not None:
        indicators.append({
            "indicator": "EMBEDDED_CREDENTIALS",
            "severity": "HIGH",
            "description": "URL contains embedded user information."
        })

    elif "@" in url:
        indicators.append({
            "indicator": "AT_SYMBOL",
            "severity": "MEDIUM",
            "description": "URL contains an @ symbol."
        })

    # 3. Excessive subdomain depth
    subdomain_parts = hostname_lower.split(".")

    if len(subdomain_parts) >= 5:
        indicators.append({
            "indicator": "EXCESSIVE_SUBDOMAINS",
            "severity": "MEDIUM",
            "description": "Hostname contains an unusually high number of labels."
        })

    # 4. URL length
    if len(url) > 200:
        indicators.append({
            "indicator": "LONG_URL",
            "severity": "LOW",
            "description": "URL length exceeds 200 characters."
        })

    if len(url) > 500:
        indicators.append({
            "indicator": "VERY_LONG_URL",
            "severity": "MEDIUM",
            "description": "URL length exceeds 500 characters."
        })

    # 5. Suspicious keywords
    url_lower = url.lower()

    matched_keywords = sorted(
        keyword
        for keyword in SUSPICIOUS_KEYWORDS
        if keyword in url_lower
    )

    if matched_keywords:
        indicators.append({
            "indicator": "SUSPICIOUS_KEYWORDS",
            "severity": "MEDIUM",
            "description": "URL contains security-sensitive keywords.",
            "keywords": matched_keywords
        })

    # 6. Punycode
    if "xn--" in hostname_lower:
        indicators.append({
            "indicator": "PUNYCODE_HOSTNAME",
            "severity": "MEDIUM",
            "description": "Hostname contains an IDN punycode label."
        })

    # 7. Non-standard port
    port = parsed.port

    if port is not None:
        default_port = (
            (parsed.scheme.lower() == "http" and port == 80)
            or
            (parsed.scheme.lower() == "https" and port == 443)
        )

        if not default_port:
            indicators.append({
                "indicator": "NON_STANDARD_PORT",
                "severity": "MEDIUM",
                "description": f"URL uses non-standard port {port}."
            })

    # 8. Query parameter count
    query_parameters = (
        parsed.query.split("&")
        if parsed.query
        else []
    )

    query_parameters = [
        item for item in query_parameters
        if item
    ]

    if len(query_parameters) >= 6:
        indicators.append({
            "indicator": "MANY_QUERY_PARAMETERS",
            "severity": "LOW",
            "description": "URL contains many query parameters.",
            "count": len(query_parameters)
        })

    # 9. URL shortener
    if hostname_lower in SHORTENER_DOMAINS:
        indicators.append({
            "indicator": "URL_SHORTENER",
            "severity": "MEDIUM",
            "description": "URL uses a known URL-shortening service."
        })

    # 10. Percent encoding
    if "%" in url:
        indicators.append({
            "indicator": "PERCENT_ENCODING",
            "severity": "LOW",
            "description": "URL contains percent-encoded characters."
        })

    # 11. Hyphen-heavy hostname
    hyphen_count = hostname.count("-")

    if hyphen_count >= 3:
        indicators.append({
            "indicator": "HYPHEN_HEAVY_HOSTNAME",
            "severity": "LOW",
            "description": "Hostname contains multiple hyphens.",
            "count": hyphen_count
        })

    return {
        "indicator_count": len(indicators),
        "indicators": indicators
    }


def main():

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE Suspicious URL Indicator Analyzer"
    )

    parser.add_argument(
        "url",
        help="URL to analyze"
    )

    args = parser.parse_args()

    try:

        result = analyze_url_indicators(args.url)

        output = {
            "status": "SUCCESS",
            "url": args.url,
            **result
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
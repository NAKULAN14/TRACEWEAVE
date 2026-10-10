from urllib.parse import urlsplit


def extract_domain_from_url(url):
    """
    Extract the hostname from a URL without
    performing a DNS or network lookup.
    """

    parsed = urlsplit(url)

    if not parsed.hostname:
        return None

    return parsed.hostname.lower()


def enrich_url_and_domain(
    provider,
    url
):
    """
    Enrich both a URL and its hostname.

    No network activity is performed by this function.
    """

    if not url:
        raise ValueError(
            "URL cannot be empty"
        )

    domain = extract_domain_from_url(
        url
    )

    url_result = provider.lookup(
        "URL",
        url
    )

    domain_result = None

    if domain:
        domain_result = provider.lookup(
            "DOMAIN",
            domain
        )

    return {
        "url": {
            "value": url,
            "enrichment": url_result,
        },

        "domain": {
            "value": domain,
            "enrichment": domain_result,
        },

        "network_access_performed": False,
    }


def main():

    import argparse
    import json

    from forensic_engine.intelligence.local_provider import (
        LocalThreatIntelligenceProvider
    )

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE URL/Domain Reputation Enricher"
        )
    )

    parser.add_argument(
        "url"
    )

    parser.add_argument(
        "--database",
        default=(
            "dataset/supplementary/"
            "threat_intelligence/local_ti.json"
        )
    )

    args = parser.parse_args()

    try:

        provider = (
            LocalThreatIntelligenceProvider(
                args.database
            )
        )

        result = enrich_url_and_domain(
            provider,
            args.url
        )

        output = {
            "status": "SUCCESS",
            **result,
        }

    except Exception as exc:

        output = {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        json.dumps(
            output,
            indent=2
        )
    )


if __name__ == "__main__":
    main()


import json
import os
from typing import Any, Dict

from forensic_engine.infrastructure.dns_provider import DNSProvider


DEFAULT_DB_PATH = os.path.join(
    "dataset",
    "supplementary",
    "threat_intelligence",
    "static_dns.json",
)


class StaticDNSProvider(DNSProvider):
    """
    Offline DNS provider backed by a JSON file.
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
    ) -> None:

        self.db_path = db_path

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"Static DNS database not found: {self.db_path}"
            )

        with open(
            self.db_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.database = json.load(file)

    @property
    def provider_name(self) -> str:
        return "STATIC_DNS"

    def resolve(
        self,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Resolve a domain using the local DNS database.
        """

        normalized_domain = (
            domain.strip()
            .lower()
            .rstrip(".")
        )

        record = self.database.get(
            normalized_domain
        )

        if record is None:
            return {
                "provider": self.provider_name,
                "status": "NOT_FOUND",
                "domain": normalized_domain,
                "records": [],
                "network_access_performed": False,
            }

        return {
            "provider": self.provider_name,
            "status": "RESOLVED",
            "domain": normalized_domain,
            "records": record.get(
                "records",
                []
            ),
            "network_access_performed": False,
        }
"""
TRACEWEAVE - Phase 14.3.2
Static TLS Certificate Provider

Provides deterministic TLS certificate evidence from a
local JSON database.

No network access is performed.
"""

import json
import os
from typing import Any, Dict

from forensic_engine.infrastructure.tls_provider import (
    TLSCertificateProvider,
)


DEFAULT_DB_PATH = os.path.join(
    "dataset",
    "supplementary",
    "threat_intelligence",
    "static_tls.json",
)


class StaticTLSCertificateProvider(
    TLSCertificateProvider
):
    """
    Offline TLS certificate provider backed by JSON.
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
    ) -> None:

        self.db_path = db_path

        if not os.path.exists(
            self.db_path
        ):
            raise FileNotFoundError(
                f"Static TLS database not found: "
                f"{self.db_path}"
            )

        with open(
            self.db_path,
            "r",
            encoding="utf-8",
        ) as file:

            self.database = json.load(
                file
            )

    @property
    def provider_name(self) -> str:
        return "STATIC_TLS"

    def get_certificate(
        self,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Retrieve certificate evidence for a domain.
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
                "provider":
                    self.provider_name,

                "status":
                    "NOT_FOUND",

                "domain":
                    normalized_domain,

                "certificate":
                    None,

                "network_access_performed":
                    False,
            }

        return {
            "provider":
                self.provider_name,

            "status":
                "FOUND",

            "domain":
                normalized_domain,

            "certificate":
                record,

            "network_access_performed":
                False,
        }
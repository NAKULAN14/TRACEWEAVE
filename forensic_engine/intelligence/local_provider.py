from pathlib import Path
import json

from forensic_engine.intelligence.provider import (
    ThreatIntelligenceProvider
)


class LocalThreatIntelligenceProvider(
    ThreatIntelligenceProvider
):
    """
    Offline deterministic threat-intelligence provider.

    The database is a controlled JSON dataset and
    does not perform any network requests.
    """

    provider_name = "LOCAL"

    def __init__(self, database_path=None):

        self.database_path = (
            Path(database_path)
            if database_path
            else None
        )

        self.database = {}

        if self.database_path:
            self._load_database()

    def _load_database(self):

        if not self.database_path.exists():
            raise FileNotFoundError(
                f"TI database not found: "
                f"{self.database_path}"
            )

        with open(
            self.database_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.database = json.load(f)

    def lookup(self, ioc_type, value):

        ioc_type = ioc_type.upper()
        value = value.strip().lower()

        type_database = self.database.get(
            ioc_type,
            {}
        )

        entry = type_database.get(
            value
        )

        if entry is None:

            return {
                "provider": self.provider_name,
                "status": "NOT_FOUND",
                "ioc_type": ioc_type,
                "value": value,
                "data": None,
            }

        return {
            "provider": self.provider_name,
            "status": "FOUND",
            "ioc_type": ioc_type,
            "value": value,
            "data": entry,
        }
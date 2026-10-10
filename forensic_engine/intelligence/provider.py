from abc import ABC, abstractmethod


class ThreatIntelligenceProvider(ABC):
    """
    Abstract interface for TRACEWEAVE
    threat-intelligence providers.
    """

    provider_name = "UNKNOWN"

    @abstractmethod
    def lookup(self, ioc_type, value):
        """
        Enrich a single IOC.

        Implementations must return a
        normalized enrichment dictionary.
        """
        raise NotImplementedError


class LocalThreatIntelligenceProvider(
    ThreatIntelligenceProvider
):
    """
    Base provider for offline/local
    threat-intelligence sources.
    """

    provider_name = "LOCAL"

    def __init__(self, database=None):
        self.database = database or {}

    def lookup(self, ioc_type, value):

        key = (
            ioc_type.upper(),
            value.lower()
        )

        result = self.database.get(
            key
        )

        if result is None:

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
            "data": result,
        }
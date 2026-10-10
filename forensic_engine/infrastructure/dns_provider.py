"""
TRACEWEAVE - Phase 14.1.1
DNS Provider Interface

Defines the common interface for DNS evidence providers.

Providers may later include:
- Static/offline DNS provider
- Live DNS provider
- Controlled test provider

This layer does not make any maliciousness determination.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class DNSProvider(ABC):
    """
    Abstract interface for DNS evidence collection.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the provider name.
        """
        raise NotImplementedError

    @abstractmethod
    def resolve(
        self,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Resolve a domain and return structured DNS evidence.

        Args:
            domain: Domain name to resolve.

        Returns:
            Structured DNS resolution result.
        """
        raise NotImplementedError
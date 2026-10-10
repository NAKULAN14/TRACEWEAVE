"""
TRACEWEAVE - Phase 14.3.1
TLS Certificate Provider Interface

Defines the common interface for TLS certificate evidence
collection.

Providers may later include:
- Static/offline certificate provider
- Live TLS certificate provider
- Controlled test provider

This layer does not determine ownership or maliciousness.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class TLSCertificateProvider(ABC):
    """
    Abstract interface for TLS certificate evidence.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the provider name.
        """
        raise NotImplementedError

    @abstractmethod
    def get_certificate(
        self,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Retrieve certificate evidence for a domain.

        Args:
            domain: Domain name associated with the certificate.

        Returns:
            Structured TLS certificate result.
        """
        raise NotImplementedError
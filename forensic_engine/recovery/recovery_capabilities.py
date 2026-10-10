from enum import Enum


class RecoveryCapability(str, Enum):
    PROPERTY_FOLDING = "PROPERTY_FOLDING"
    CONTAINER_BOUNDARY = "CONTAINER_BOUNDARY"
    ENCODING_STRUCTURE = "ENCODING_STRUCTURE"
    TRUNCATION = "TRUNCATION"
    COMPONENT_BOUNDARY = "COMPONENT_BOUNDARY"


RECOVERY_CAPABILITY_MAP = {
    "TW-ICS-003": [
        RecoveryCapability.PROPERTY_FOLDING
    ],
    "TW-ICS-004": [
        RecoveryCapability.CONTAINER_BOUNDARY
    ],
    "TW-ICS-009": [
        RecoveryCapability.ENCODING_STRUCTURE
    ],
    "TW-ICS-015": [
        RecoveryCapability.TRUNCATION
    ],
    "TW-ICS-016": [
        RecoveryCapability.TRUNCATION,
        RecoveryCapability.COMPONENT_BOUNDARY
    ],
}


def get_capabilities(case_id: str):
    return RECOVERY_CAPABILITY_MAP.get(case_id, [])
from enum import Enum

class RepositoryVisibility(Enum):
    """
    Enum representing the visibility of a GitHub repository
    UNKNOWN is used when the visibility cannot be determined (e.g., due to API limitations or errors)
    """

    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"
    UNKNOWN = "unknown"

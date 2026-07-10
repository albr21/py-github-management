from enum import Enum

class BaseRole(Enum):
    """
    Enum representing the base role that a custom role can extend
    """

    READ = "read"
    TRIAGE = "triage"
    WRITE = "write"
    MAINTAIN = "maintain"

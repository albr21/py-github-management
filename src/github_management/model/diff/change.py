from dataclasses import dataclass
from typing import Any
from .change_type import ChangeType
from .color import Color

@dataclass
class Change:
    """A single difference between local and remote."""
    path: str
    type: ChangeType
    local: Any
    remote: Any

    def __str__(self):
        match self.type:
            case ChangeType.ADDED:
                return f"{Color.GREEN}+ {self.path}: {self.local}{Color.RESET}"
            case ChangeType.REMOVED:
                return f"{Color.RED}- {self.path}: {self.remote}{Color.RESET}"
            case ChangeType.CHANGED:
                return (
                    f"{Color.YELLOW}~ {self.path}:{Color.RESET}\n"
                    f"  {Color.RED}- remote: {self.remote}{Color.RESET}\n"
                    f"  {Color.GREEN}+ local:  {self.local}{Color.RESET}"
                )

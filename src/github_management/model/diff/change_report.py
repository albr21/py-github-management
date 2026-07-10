from .change import Change
from .color import Color

class ChangeReport:
    """
    A report of differences between local and remote GitHub objects.
    """

    def __init__(self, changes: list[Change]) -> None:
        self.changes = changes

    def has_changes(self):
        return bool(self.changes)

    def __str__(self):
        if not self.changes:
            return f"{Color.GREEN}✅ No differences found.{Color.RESET}"
        report = f"{Color.YELLOW}📋 Found {len(self.changes)} difference(s):{Color.RESET}\n\n"
        report += "\n".join(str(change) for change in self.changes)
        return report

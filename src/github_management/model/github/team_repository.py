from .github_object import GitHubObject
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType

class TeamRepository(GitHubObject):
    """
    Class representing a GitHub team repository
    """

    # @param name [str]: Name of the repository
    # @param role [str]: Role of the team in the repository
    def __init__(self, *, name: str, role: str) -> None:
        self.name = name
        self.role = role

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamRepository":
        return cls(name=data["name"], role=data["role"])

    def diff(self, other: "TeamRepository", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.role != other.role:
            changes.append(Change(f"{path}.role", ChangeType.CHANGED, self.role, other.role))
        return changes

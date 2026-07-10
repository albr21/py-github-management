from github import NamedUser as GitHubNamedUser

from .github_object import GitHubObject
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType

class Member(GitHubObject):
    """
    Class representing a GitHub member
    """

    # @param login [str]: Login of the member
    # @param name [str]: Name of the member
    # @param email [str]: Email of the member
    def __init__(self, *, login: str, name: str) -> None:
        self.login = login
        self.name = name

    @classmethod
    def fetch_from_github(cls, client, login: str) -> "Member":
        github_member = client.client.get_user(login)
        name = github_member.name
        return cls(login=login, name=name)

    @classmethod
    def from_github_object(cls, github_object: GitHubNamedUser) -> "Member":
        return cls(login=github_object.login, name=github_object.name)

    def to_dict(self) -> dict:
        return {
            "login": self.login,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        return cls(login=data["login"], name=data["name"])

    def diff(self, other: "Member", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.name != other.name:
            changes.append(Change(f"{path}.name", ChangeType.CHANGED, self.name, other.name))
        return changes

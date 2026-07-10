from .github_object import GitHubObject
from .repository import Repository
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType
from ...model.diff.utils import diff_list_by_name
from ...client import Client

class User(GitHubObject):
    """
    Class representing User in GitHub
    """

    # @param name [str]: Name of the user
    # @param repositories [List[Repository] | None]: List of repositories in the organization
    def __init__(self, *, name: str, repositories: list[Repository] = None) -> None:
        self.name = name
        self.repositories = repositories if repositories is not None else []

    @classmethod
    def fetch_from_github(cls, *, client: Client) -> "User":
        github_user = client.client.get_user()
        name = github_user.login
        repositories = [Repository.from_github_object(repo) for repo in github_user.get_repos(affiliation="owner")]
        return cls(name=name, repositories=repositories)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "repositories": [repo.to_dict() for repo in self.repositories]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        name = data["name"]
        repositories = [Repository.from_dict(repo_data) for repo_data in data.get("repositories", [])]
        return cls(name=name, repositories=repositories)

    def diff(self, other: "User", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.name != other.name:
            changes.append(Change(f"{path}.name", ChangeType.CHANGED, self.name, other.name))
        changes.extend(diff_list_by_name(self.repositories, other.repositories, f"{path}.repositories"))
        return changes

    def push_repositories_to_github(
            self,
            client: Client,
            repo_filter: list[str] = None,
            fields: set[str] | None = None,
            dry_run: bool = False
        ) -> None:

        for repo in self.repositories:
            if repo_filter and repo.name not in repo_filter:
                continue
            repo.push_to_github(client=client, fields=fields, dry_run=dry_run)

    def cleanup_collaborators(
            self,
            client: Client,
            remove_members: list[str] | None = None,
            auto_delete_inactive: bool = False,
            dry_run: bool = False
        ) -> None:

        for repo in self.repositories:
            repo.cleanup_collaborators(
                client=client,
                remove_members=remove_members,
                auto_delete_inactive=auto_delete_inactive,
                dry_run=dry_run
            )

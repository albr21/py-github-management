from github import Repository as GitHubRepository
from github.GithubException import UnknownObjectException
from .github_object import GitHubObject
from .repository_permissions import RepositoryPermissions
from .repository_visibility import RepositoryVisibility
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType
from ...model.diff.utils import diff_set
from ...client import Client

class Repository(GitHubObject):
    """
    Class representing a GitHub repository
    """

    # @param name [str]: Name of the repository
    # @param owner [str]: Owner of the repository (user or organization)
    # @param description [str]: Description of the repository
    # @param topics [List[str] | None]: List of topics associated with the repository
    # @param permissions [Permission | None]: Permissions for the repository, if any
    def __init__(
            self,
            *,
            name: str,
            owner: str,
            description: str = "",
            archive: bool = False,
            visibility: RepositoryVisibility = RepositoryVisibility.UNKNOWN,
            topics: list[str] = None,
            permissions: RepositoryPermissions | None = None
        ) -> None:

        self.name = name
        self.owner = owner
        self.description = description
        self.archive = archive
        self.visibility = visibility
        self.topics = topics if topics is not None else []
        self.permissions = permissions

    def push_to_github(self, client: Client, fields: set[str] | None = None, dry_run: bool = False) -> None:
        """
        Push local state to GitHub.
        If fields is None, all supported fields are pushed.
        Otherwise, only the specified fields are pushed (e.g., {"description", "topics"}).
        Supported fields: description, topics
        Other field values are skipped.
        """

        github_repo = client.client.get_repo(f"{self.owner}/{self.name}")

        edit_kwargs = {}
        if fields is None or "description" in fields:
            edit_kwargs["description"] = self.description

        if edit_kwargs:
            if not dry_run:
                github_repo.edit(**edit_kwargs)
            else:
                print(f"DRY RUN: Would edit repository '{self.name}' with {edit_kwargs}")

        if fields is None or "topics" in fields:
            if not dry_run:
                github_repo.replace_topics(self.topics)
            else:
                print(f"DRY RUN: Would replace topics for repository '{self.name}' with {self.topics}")

    def cleanup_collaborators(
            self,
            client: Client,
            remove_members: list[str] | None = None,
            auto_delete_inactive: bool = False,
            dry_run: bool = False
        ) -> None:

        if self.permissions is None:
            return

        github_repo = client.client.get_repo(f"{self.owner}/{self.name}")

        if auto_delete_inactive:
            for login in self.permissions.all_logins():
                try:
                    client.client.get_user(login)
                except UnknownObjectException:
                    # pylint: disable=C0301
                    print(f"[user cleanup] Collaborator '{login}' no longer exists on GitHub - removing from repo '{self.name}'")
                    # pylint: enable=C0301
                    if not dry_run:
                        github_repo._requester.requestJsonAndCheck(
                            "DELETE",
                            f"{github_repo.url}/collaborators/{login}",
                        )

        if remove_members:
            for login in remove_members:
                if login in self.permissions.all_logins():
                    print(f"[user cleanup] Removing collaborator '{login}' from repo '{self.name}'")
                    if not dry_run:
                        try:
                            user = client.client.get_user(login)
                            github_repo.remove_from_collaborators(user)
                        except UnknownObjectException:
                            print(f"[user cleanup] Warning: user '{login}' not found on GitHub")

    @classmethod
    def from_github_object(cls, github_object: GitHubRepository) -> "Repository":
        name = github_object.name
        owner = github_object.owner.login
        description = github_object.description
        topics = github_object.get_topics()
        archive = github_object.archived
        match github_object.visibility:
            case "public":
                visibility = RepositoryVisibility.PUBLIC
            case "private":
                visibility = RepositoryVisibility.PRIVATE
            case "internal":
                visibility = RepositoryVisibility.INTERNAL
            case _:
                visibility = RepositoryVisibility.UNKNOWN

        permissions = RepositoryPermissions.from_github_object(github_object)

        return cls(
            name=name,
            owner=owner,
            description=description,
            archive=archive,
            visibility=visibility,
            topics=topics,
            permissions=permissions
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "archive": self.archive,
            "visibility": self.visibility.value,
            "topics": self.topics,
            "permissions": self.permissions.to_dict() if self.permissions else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Repository":
        permissions = RepositoryPermissions.from_dict(data["permissions"]) if data.get("permissions") else None
        visibility_value = data.get("visibility")
        if visibility_value is not None:
            visibility = RepositoryVisibility(visibility_value)
        else:
            visibility = RepositoryVisibility.UNKNOWN
        return cls(
            name=data["name"],
            owner=data["owner"],
            description=data.get("description", ""),
            archive=data.get("archive", False),
            visibility=visibility,
            topics=data.get("topics", []),
            permissions=permissions
        )

    def diff(self, other: "Repository", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.owner != other.owner:
            changes.append(Change(f"{path}.owner", ChangeType.CHANGED, self.owner, other.owner))
        if self.description != other.description:
            changes.append(Change(f"{path}.description", ChangeType.CHANGED, self.description, other.description))
        if self.archive != other.archive:
            changes.append(Change(f"{path}.archive", ChangeType.CHANGED, self.archive, other.archive))
        if self.visibility != other.visibility:
            changes.append(
                Change(f"{path}.visibility", ChangeType.CHANGED, self.visibility.value, other.visibility.value)
            )
        changes.extend(diff_set(self.topics, other.topics, f"{path}.topics"))
        if self.permissions and other.permissions:
            changes.extend(self.permissions.diff(other.permissions, f"{path}.permissions"))
        elif self.permissions and not other.permissions:
            changes.append(Change(f"{path}.permissions", ChangeType.ADDED, self.permissions, None))
        elif not self.permissions and other.permissions:
            changes.append(Change(f"{path}.permissions", ChangeType.REMOVED, None, other.permissions))
        return changes

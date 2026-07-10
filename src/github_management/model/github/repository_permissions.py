from github import Repository as GitHubRepository
from github.GithubException import UnknownObjectException

from .github_object import GitHubObject
from ...model.diff.change import Change
from ...model.diff.utils import diff_set

class RepositoryPermissions(GitHubObject):
    """
    Class representing a GitHub permission
    """

    # @param admin [List[str] | None]: List of logins of users/teams with admin permissions
    # @param maintain [List[str] | None]: List of logins of users/teams with maintain permissions
    # @param write [List[str] | None]: List of logins of users/teams with push permissions
    # @param triage [List[str] | None]: List of logins of users/teams with triage permissions
    # @param read [List[str] | None]: List of logins of users/teams with pull permissions
    def __init__(
            self,
            *,
            admin: list[str] = None,
            maintain: list[str] = None,
            write: list[str] = None,
            triage: list[str] = None,
            read: list[str] = None
        ) -> None:

        self.admin = admin if admin is not None else []
        self.maintain = maintain if maintain is not None else []
        self.write = write if write is not None else []
        self.triage = triage if triage is not None else []
        self.read = read if read is not None else []

    @classmethod
    def from_github_object(cls, github_object: GitHubRepository) -> "RepositoryPermissions":
        admin = []
        maintain = []
        write = []
        triage = []
        read = []

        print(f"Fetching permissions for repository {github_object.full_name}...")

        for user in github_object.get_collaborators():
            permissions = user.permissions
            if permissions.admin:
                admin.append(user.login)
            elif permissions.maintain:
                maintain.append(user.login)
            elif permissions.push:
                write.append(user.login)
            elif permissions.triage:
                triage.append(user.login)
            elif permissions.pull:
                read.append(user.login)
        try:
            for team in github_object.get_teams():
                permissions = team.permissions
                if permissions.admin:
                    admin.append(team.name)
                elif permissions.maintain:
                    maintain.append(team.name)
                elif permissions.push:
                    write.append(team.name)
                elif permissions.triage:
                    triage.append(team.name)
                elif permissions.pull:
                    read.append(team.name)
        except UnknownObjectException:
            # If the repository isn't part of an organization, get_teams() will
            # throw an UnknownObjectException. In that case, team permissions
            # are ignored.
            pass
        return cls(admin=admin, maintain=maintain, write=write, triage=triage, read=read)

    def to_dict(self) -> dict:
        return {
            "admin": self.admin,
            "maintain": self.maintain,
            "write": self.write,
            "triage": self.triage,
            "read": self.read
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RepositoryPermissions":
        return cls(
            admin=data.get("admin", []),
            maintain=data.get("maintain", []),
            write=data.get("write", []),
            triage=data.get("triage", []),
            read=data.get("read", [])
        )

    def all_logins(self) -> list[str]:
        return self.admin + self.maintain + self.write + self.triage + self.read

    def diff(self, other: "RepositoryPermissions", path: str = "") -> list[Change]:
        changes: list[Change] = []
        for level in ("admin", "maintain", "write", "triage", "read"):
            changes.extend(diff_set(
                getattr(self, level),
                getattr(other, level),
                f"{path}.{level}",
            ))
        return changes

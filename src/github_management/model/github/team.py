from .github_object import GitHubObject
from .team_repository import TeamRepository
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType
from ...model.diff.utils import diff_set, diff_list_by_name
from ...client import Client

# GitHub API returns friendly role names in GET (role_name) but expects legacy names in PUT (permission)
_ROLE_TO_PERMISSION = {
    "read": "pull",
    "write": "push",
    "triage": "triage",
    "maintain": "maintain",
    "admin": "admin",
}

def _to_api_permission(role: str) -> str:
    return _ROLE_TO_PERMISSION.get(role, role)

class Team(GitHubObject):
    """
    Class representing a GitHub team
    """

    # @param name [str]: Name of the team
    # @param description [str]: Description of the team
    # @param members [List[str] | None]: List of logins of the members in the team
    # @param parent [str | None]: Name of the parent team, if any
    # @param repositories [List[TeamRepository] | None]: List of repositories associated with the team and
    #                                                    the role of the team in each repository
    def __init__(
            self,
            *,
            name: str,
            description: str = "",
            members: list[str] | None = None,
            parent: str | None = None,
            repositories: list[TeamRepository] | None = None
        ) -> None:

        self.name = name
        self.description = description
        self.members = members if members is not None else []
        self.parent = parent
        self.repositories = repositories if repositories is not None else []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "members": self.members,
            "parent": self.parent,
            "repositories": [repo.to_dict() for repo in self.repositories]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        repositories = [TeamRepository.from_dict(repo_data) for repo_data in data.get("repositories", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            members=data.get("members", []),
            parent=data.get("parent"),
            repositories=repositories
        )

    def diff(self, other: "Team", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.description != other.description:
            changes.append(Change(f"{path}.description", ChangeType.CHANGED, self.description, other.description))
        if self.parent != other.parent:
            changes.append(Change(f"{path}.parent", ChangeType.CHANGED, self.parent, other.parent))
        changes.extend(diff_set(self.members, other.members, f"{path}.members"))
        changes.extend(diff_list_by_name(self.repositories, other.repositories, f"{path}.repositories"))
        return changes

    def push_to_github(
            self,
            *,
            client: Client,
            github_org,
            github_team,
            current_github_teams: dict,
            dry_run: bool = False
        ) -> None:
        """Sync this team's metadata, members, and repository permissions to GitHub."""
        # Metadata
        current_description = github_team.description or ""
        current_parent = github_team.parent.name if github_team.parent else None
        if self.description != current_description or self.parent != current_parent:
            # pylint: disable=C0301
            parent_team_id = current_github_teams[self.parent].id if self.parent and self.parent in current_github_teams else None
            # pylint: enable=C0301
            print(f"[push teams] Updating metadata of team '{self.name}'")
            if not dry_run:
                edit_kwargs: dict = {"description": self.description}
                if parent_team_id is not None:
                    edit_kwargs["parent_team_id"] = parent_team_id
                github_team.edit(self.name, **edit_kwargs)

        # Members
        current_members = {m.login for m in github_team.get_members()}
        desired_members = set(self.members)
        for login in sorted(desired_members - current_members):
            print(f"[push teams] Adding member '{login}' to team '{self.name}'")
            if not dry_run:
                github_team.add_to_members(client.client.get_user(login))
        for login in sorted(current_members - desired_members):
            print(f"[push teams] Removing member '{login}' from team '{self.name}'")
            if not dry_run:
                github_team.remove_from_members(client.client.get_user(login))

        # Repositories
        repos_response = github_team._requester.requestJsonAndCheck(
            "GET",
            f"{github_team.url}/repos",
            headers={"Accept": "application/vnd.github.v3.repository+json"},
        )
        current_repos = {r["name"]: r.get("role_name") for r in repos_response[1]}
        desired_repos = {r.name: r.role for r in self.repositories}
        org_login = github_org.login

        for name in sorted(set(desired_repos) - set(current_repos)):
            print(f"[push teams] Adding repo '{name}' to team '{self.name}' with role '{desired_repos[name]}'")
            if not dry_run:
                github_team._requester.requestJsonAndCheck(
                    "PUT",
                    f"{github_team.url}/repos/{org_login}/{name}",
                    input={"permission": _to_api_permission(desired_repos[name])}
                )
        for name in sorted(set(current_repos) - set(desired_repos)):
            print(f"[push teams] Removing repo '{name}' from team '{self.name}'")
            if not dry_run:
                github_team._requester.requestJsonAndCheck("DELETE", f"{github_team.url}/repos/{org_login}/{name}")
        for name in sorted(set(desired_repos) & set(current_repos)):
            if desired_repos[name] != current_repos[name]:
                # pylint: disable=C0301
                print(f"[push teams] Updating repo '{name}' role in team '{self.name}': '{current_repos[name]}' - '{desired_repos[name]}'")
                # pylint: enable=C0301
                if not dry_run:
                    github_team._requester.requestJsonAndCheck(
                        "PUT",
                        f"{github_team.url}/repos/{org_login}/{name}",
                        input={"permission": _to_api_permission(desired_repos[name])}
                    )

    def create_in_github(
            self,
            *,
            client: Client,
            github_org,
            current_github_teams: dict,
            dry_run: bool = False
        ) -> None:
        """Create this team in the GitHub organization and populate its members and repository permissions."""
        print(f"[push teams] Creating team '{self.name}' in org '{github_org.login}'")
        if dry_run:
            return

        # pylint: disable=C0301
        parent_team_id = current_github_teams[self.parent].id if self.parent and self.parent in current_github_teams else None
        # pylint: enable=C0301
        create_kwargs: dict = {"name": self.name, "description": self.description, "privacy": "closed"}
        if parent_team_id is not None:
            create_kwargs["parent_team_id"] = parent_team_id

        github_team = github_org.create_team(**create_kwargs)
        # Register in the dict so subsequent child teams can resolve this parent
        current_github_teams[self.name] = github_team

        for login in sorted(self.members):
            github_team.add_to_members(client.client.get_user(login))
        for team_repo in self.repositories:
            github_team._requester.requestJsonAndCheck(
                "PUT",
                f"{github_team.url}/repos/{github_org.login}/{team_repo.name}",
                input={"permission": _to_api_permission(team_repo.role)},
            )

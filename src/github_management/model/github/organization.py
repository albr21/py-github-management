import fnmatch
from github.GithubException import UnknownObjectException
from .team_repository import TeamRepository
from .github_object import GitHubObject
from .member import Member
from .repository import Repository
from .role import Role
from .team import Team
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType
from ...model.diff.utils import diff_list_by_name, diff_list_by_login
from ...client import Client

class Organization(GitHubObject):
    """
    Class representing a GitHub organization
    """

    # @param name [str]: Name of the organization
    # @param description [str]: Description of the organization
    # @param members [List[Member] | None]: List of members in the organization
    # @param teams [List[Team] | None]: List of teams in the organization
    # @param repositories [List[Repository] | None]: List of repositories in the organization
    # @param roles [List[Role] | None]: List of roles in the organization
    def __init__(
            self,
            *,
            name: str,
            description: str = "",
            members: list[Member] = None,
            teams: list[Team] = None,
            repositories: list[Repository] = None,
            roles: list[Role] = None
        ) -> None:

        self.name = name
        self.description = description
        self.members = members if members is not None else []
        self.repositories = repositories if repositories is not None else []
        self.roles = roles if roles is not None else []
        self.teams = teams if teams is not None else []

    @classmethod
    def fetch_from_github(cls, *, client: Client, name: str) -> "Organization":
        github_organization = client.client.get_organization(name)
        description = github_organization.description
        members = [Member.from_github_object(member) for member in github_organization.get_members()]
        roles = cls.__fetch_roles_from_github(client, name)
        repositories = [Repository.from_github_object(repo) for repo in github_organization.get_repos()]
        teams = cls._fetch_teams_from_github(github_organization)
        return cls(
            name=name,
            description=description,
            members=members,
            repositories=repositories,
            roles=roles,
            teams=teams
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "members": [member.to_dict() for member in self.members],
            "teams": [team.to_dict() if team else None for team in self.teams],
            "roles": [role.to_dict() for role in self.roles],
            "repositories": [repo.to_dict() for repo in self.repositories]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Organization":
        name = data["name"]
        description = data.get("description", "")
        members = [Member.from_dict(member_data) for member_data in data.get("members", [])]
        teams = [Team.from_dict(team_data) if team_data else None for team_data in data.get("teams", [])]
        roles = [Role.from_dict(role_data) for role_data in data.get("roles", [])]
        repositories = [Repository.from_dict(repo_data) for repo_data in data.get("repositories", [])]
        return cls(
            name=name,
            description=description,
            members=members,
            teams=teams,
            roles=roles,
            repositories=repositories
        )

    def diff(self, other: "Organization", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.description != other.description:
            changes.append(Change(f"{path}.description", ChangeType.CHANGED, self.description, other.description))
        changes.extend(diff_list_by_login(self.members, other.members, f"{path}.members"))
        changes.extend(diff_list_by_name(self.repositories, other.repositories, f"{path}.repositories"))
        changes.extend(diff_list_by_name([t for t in self.teams if t], [t for t in other.teams if t], f"{path}.teams"))
        changes.extend(diff_list_by_name(self.roles, other.roles, f"{path}.roles"))
        return changes

    @classmethod
    def __fetch_roles_from_github(cls, client: Client, organization_name: str) -> list[Role]:
        """
        Fetch roles from GitHub API (not directly available via PyGithub, use GitHub REST API)
        """
        # pylint: disable=C0301
        predefined_roles = [
            Role(name="read", description="Can read and clone this repository.", permissions=[]),
            Role(name="triage", description="Can read and clone this repository. Can also manage issues and pull requests.", permissions=[]),
            Role(name="write", description="Can read, clone, and push to this repository. Can also manage issues and pull requests.", permissions=[]),
            Role(name="maintain", description="Can read, clone, and push to this repository. Can also manage issues, pull requests, and some repository settings.", permissions=[]),
            Role(name="admin", description="Full access to this repository.", permissions=[]),
        ]
        # pylint: enable=C0301

        org = client.client.get_organization(organization_name)
        try:
            response = org._requester.requestJsonAndCheck(
                "GET",
                f"{org.url}/custom-repository-roles",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            custom_roles = [Role.from_dict(role) for role in response[1]["custom_roles"]]
            return predefined_roles + custom_roles
        except Exception as e:
            print(f"Error fetching roles from GitHub API: {e}")
            return []

    @classmethod
    def _fetch_teams_from_github(cls, github_organization: object) -> list[Team]:
        teams = []
        for team in github_organization.get_teams():
            team_repositories = []

            response = team._requester.requestJsonAndCheck(
                "GET",
                f"{team.url}/repos",
                headers={"Accept": "application/vnd.github.v3.repository+json"}
            )
            repos_data = response[1]

            for repo_data in repos_data:
                role = repo_data.get("role_name", None)
                team_repositories.append(TeamRepository(name=repo_data["name"], role=role))

            teams.append(
                Team(
                    name=team.name,
                    description=team.description,
                    members=[member.login for member in team.get_members()],
                    parent=team.parent.name if team.parent else None,
                    repositories=team_repositories
                )
            )
        return teams

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

    def cleanup_members(
            self,
            client: Client,
            remove_members: list[str] | None = None,
            auto_delete_inactive: bool = False,
            dry_run: bool = False
        ) -> None:

        github_org = client.client.get_organization(self.name)

        if auto_delete_inactive:
            for member in self.members:
                try:
                    client.client.get_user(member.login)
                except UnknownObjectException:
                    # pylint: disable=C0301
                    print(f"[org cleanup] Member '{member.login}' no longer exists on GitHub - removing from org '{self.name}'")
                    # pylint: enable=C0301
                    if not dry_run:
                        github_org._requester.requestJsonAndCheck(
                            "DELETE",
                            f"{github_org.url}/members/{member.login}",
                        )

        if remove_members:
            for login in remove_members:
                print(f"[org cleanup] Removing member '{login}' from org '{self.name}'")
                if not dry_run:
                    try:
                        user = client.client.get_user(login)
                        github_org.remove_from_members(user)
                    except UnknownObjectException:
                        print(f"[org cleanup] Warning: user '{login}' not found on GitHub")

    def push_teams_to_github(self, client: Client, team_filter: str | None = None, dry_run: bool = False) -> None:
        """Create, update, and delete teams in this organization to match the local YAML state."""
        github_org = client.client.get_organization(self.name)
        current_github_teams = {t.name: t for t in github_org.get_teams()}

        local_teams = [t for t in self.teams if t and (team_filter is None or fnmatch.fnmatch(t.name, team_filter))]
        local_team_names = {t.name for t in local_teams}

        # Parents before children so newly created parents can be resolved for their children
        local_teams.sort(key=lambda t: (t.parent is not None, t.parent or ""))

        for team in local_teams:
            if team.name not in current_github_teams:
                team.create_in_github(
                    client=client,
                    github_org=github_org,
                    current_github_teams=current_github_teams,
                    dry_run=dry_run
                )
            else:
                print(f"[push teams] Syncing team '{team.name}' in org '{self.name}'")
                team.push_to_github(
                    client=client,
                    github_org=github_org,
                    github_team=current_github_teams[team.name],
                    current_github_teams=current_github_teams,
                    dry_run=dry_run
                )

        teams_to_delete = [
            (name, github_team)
            for name, github_team in current_github_teams.items()
            if (team_filter is None or fnmatch.fnmatch(name, team_filter)) and name not in local_team_names
        ]
        # Delete children before parents to avoid cascade deletions causing 404s
        teams_to_delete.sort(key=lambda t: (t[1].parent is None, t[0]))

        for name, github_team in teams_to_delete:
            print(f"[push teams] Deleting team '{name}' from org '{self.name}'")
            if not dry_run:
                github_team.delete()

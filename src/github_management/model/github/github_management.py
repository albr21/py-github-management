import yaml
from .user import User
from .organization import Organization
from ...client import Client
from ..diff.change_report import ChangeReport
from ..diff.utils import diff_list_by_name

class GitHubManagement:
    """
    Head class for GitHub management
    """

    # @param organizations [List[Organization]]: List of organizations to manage
    def __init__(self, *, user: User, organizations: list[Organization] = None) -> None:
        self.user = user
        self.organizations = organizations if organizations is not None else []

    @classmethod
    def fetch_from_github(cls, *, client: Client, organization_names: list[str]) -> "GitHubManagement":
        if not organization_names:
            print("No organization names provided. Fetching only user data.")
            organizations_instance = []
        else:
            organizations_instance = [
            Organization.fetch_from_github(client=client, name=name) for name in organization_names
            ]
        user_instance = User.fetch_from_github(client=client)

        return cls(user=user_instance, organizations=organizations_instance)

    def to_dict(self) -> dict:
        return {
            "user": self.user.to_dict(),
            "organizations": [org.to_dict() for org in self.organizations]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GitHubManagement":
        user = User.from_dict(data.get("user", {}))
        organizations = [Organization.from_dict(org_data) for org_data in data.get("organizations", [])]
        return cls(user=user, organizations=organizations)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "GitHubManagement":
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    def diff(self, other: "GitHubManagement") -> ChangeReport:
        changes = diff_list_by_name(self.organizations, other.organizations, "organizations")
        return ChangeReport(changes=changes)

    def push_repositories_to_github_for_orgs(
            self,
            client: Client,
            org_filter: list[str] = None,
            repo_filter: list[str] = None,
            fields: set[str] | None = None,
            dry_run: bool = False
        ) -> None:

        for org in self.organizations:
            if org_filter and org.name not in org_filter:
                continue
            print(f"Pushing repositories for organization: {org.name}")
            org.push_repositories_to_github(client=client, repo_filter=repo_filter, fields=fields, dry_run=dry_run)

    def push_repositories_to_github_for_user(
            self,
            client: Client,
            repo_filter: list[str] = None,
            fields: set[str] | None = None,
            dry_run: bool = False
        ) -> None:

        self.user.push_repositories_to_github(client=client, repo_filter=repo_filter, fields=fields, dry_run=dry_run)

    def cleanup_org_members(
            self,
            client: Client,
            remove_members: list[str] | None = None,
            auto_delete_inactive: bool = False,
            dry_run: bool = False
        ) -> None:

        for org in self.organizations:
            print(f"Cleaning up members for organization: {org.name}")
            org.cleanup_members(
                client=client,
                remove_members=remove_members,
                auto_delete_inactive=auto_delete_inactive,
                dry_run=dry_run
            )

    def cleanup_user_collaborators(
            self,
            client: Client,
            remove_members: list[str] | None = None,
            auto_delete_inactive: bool = False,
            dry_run: bool = False
        ) -> None:

        self.user.cleanup_collaborators(
            client=client,
            remove_members=remove_members,
            auto_delete_inactive=auto_delete_inactive,
            dry_run=dry_run
        )

    def push_teams_to_github_for_orgs(
            self,
            client: Client,
            org_filter: list[str] | None = None,
            team_filter: str | None = None,
            dry_run: bool = False
        ) -> None:

        for org in self.organizations:
            if org_filter and org.name not in org_filter:
                continue
            print(f"Pushing teams for organization: {org.name}")
            org.push_teams_to_github(client=client, team_filter=team_filter, dry_run=dry_run)

from dataclasses import dataclass
import yaml
from .branch_protection import BranchProtection
from .pr_configuration import PRConfiguration
from ....client import Client

@dataclass
class Configuration:
    """
    Configuration to create a repository with, based on a template repository.
    """

    template_repository: str
    name: str
    description: str = ""
    private: bool = False
    has_wiki: bool = False
    has_projects: bool = False
    include_all_branches: bool = False
    branch_protection: BranchProtection | None = None
    pr_configuration: PRConfiguration | None = None

    def to_dict(self) -> dict:
        return {
            "template_repository": self.template_repository,
            "name": self.name,
            "description": self.description,
            "private": self.private,
            "has_wiki": self.has_wiki,
            "has_projects": self.has_projects,
            "include_all_branches": self.include_all_branches,
            "branch_protection": self.branch_protection.to_dict() if self.branch_protection else None,
            "pr_configuration": self.pr_configuration.to_dict() if self.pr_configuration else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Configuration":
        template_repository = data.get("template_repository", "")
        name = data.get("name", "")
        description = data.get("description", "")
        private = data.get("private", False)
        has_wiki = data.get("has_wiki", False)
        has_projects = data.get("has_projects", False)
        include_all_branches = data.get("include_all_branches", False)
        branch_protection_data = data.get("branch_protection")
        pr_configuration_data = data.get("pr_configuration")

        branch_protection = BranchProtection.from_dict(branch_protection_data) if branch_protection_data else None
        pr_configuration = PRConfiguration.from_dict(pr_configuration_data) if pr_configuration_data else None

        return cls(
            template_repository=template_repository,
            name=name,
            description=description,
            private=private,
            has_wiki=has_wiki,
            has_projects=has_projects,
            include_all_branches=include_all_branches,
            branch_protection=branch_protection,
            pr_configuration=pr_configuration
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Configuration":
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    def __str__(self):
        """
        String representation of the object
        """
        kv = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{self.__class__.__name__}({kv})"

    def create(self, client: Client) -> None:
        """
        Create a repository in GitHub using the configuration.
        """

        user = client.client.get_user()
        github_template_repository = client.client.get_repo(self.template_repository)
        github_created_repository = user.create_repo_from_template(
            name=self.name,
            repo=github_template_repository,
            description=self.description,
            private=self.private,
            include_all_branches=self.include_all_branches
        )

        github_created_repository.edit(
            has_wiki=self.has_wiki,
            has_projects=self.has_projects
        )

        if self.branch_protection:
            self.branch_protection.apply(github_repository=github_created_repository)

        if self.pr_configuration:
            self.pr_configuration.apply(github_repository=github_created_repository)

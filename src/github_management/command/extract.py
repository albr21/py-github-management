from ..client import Client
from ..model.github.github_management import GitHubManagement
from .utils import save

def extract(client: Client, args) -> None:
    """Extract organization data from GitHub and write to YAML."""
    github_management = GitHubManagement.fetch_from_github(client=client, organization_names=args.orgs)
    save(args.file, github_management.to_yaml())

    print(f"Data extracted and saved to {args.file}")

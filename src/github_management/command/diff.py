from ..client import Client
from ..model.github.github_management import GitHubManagement
from .utils import load_github_management_yaml

def diff(client: Client, args) -> None:
    """Diff local YAML against live GitHub state."""
    local = load_github_management_yaml(args.file)
    remote = GitHubManagement.fetch_from_github(client=client, organization_names=args.orgs)

    changes = local.diff(remote)
    print(changes)

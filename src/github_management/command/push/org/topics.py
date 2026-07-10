from ....client import Client
from ...utils import load_github_management_yaml

def push_org_topics(client: Client, args) -> None:
    """Push organization repository topics, optionally filtered by repo name."""
    local = load_github_management_yaml(args.file)

    org_filter = args.orgs
    repo_filter = args.repo_filter

    if args.dry_run:
        print("[push organization topics] DRY RUN — no changes will be applied")

    local.push_repositories_to_github_for_orgs(
        client=client,
        org_filter=org_filter,
        repo_filter=repo_filter,
        fields={"topics"},
        dry_run=args.dry_run
    )

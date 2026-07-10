from ....client import Client
from ...utils import load_github_management_yaml

def push_user_topics(client: Client, args) -> None:
    """Push user repository topics, optionally filtered by repo name."""
    local = load_github_management_yaml(args.file)

    repo_filter = args.repo_filter

    if args.dry_run:
        print("[push user topics] DRY RUN — no changes will be applied")

    local.push_repositories_to_github_for_user(
        client=client,
        repo_filter=repo_filter,
        fields={"topics"},
        dry_run=args.dry_run
    )

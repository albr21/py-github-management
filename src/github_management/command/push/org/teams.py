from ....client import Client
from ...utils import load_github_management_yaml

def push_org_teams(client: Client, args) -> None:
    """Push teams modifications for all organizations (create, update, delete)."""
    local = load_github_management_yaml(args.file)

    org_filter = args.orgs
    team_filter = args.team_filter

    if args.dry_run:
        print("[push org teams] DRY RUN — no changes will be applied")

    local.push_teams_to_github_for_orgs(
        client=client,
        org_filter=org_filter,
        team_filter=team_filter,
        dry_run=args.dry_run,
    )

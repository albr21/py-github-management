from ....client import Client
from ...utils import load_github_management_yaml

def push_org_cleanup(client: Client, args) -> None:
    """Cleanup organization members."""
    local = load_github_management_yaml(args.file)

    if args.dry_run:
        print("[push org cleanup] DRY RUN — no changes will be applied")

    local.cleanup_org_members(
        client=client,
        remove_members=args.remove_member,
        auto_delete_inactive=args.auto_delete_inactive,
        dry_run=args.dry_run,
    )

from ....client import Client
from ...utils import load_github_management_yaml

def push_user_cleanup(client: Client, args) -> None:
    """Cleanup user repository collaborators."""
    local = load_github_management_yaml(args.file)

    if args.dry_run:
        print("[push user cleanup] DRY RUN — no changes will be applied")

    local.cleanup_user_collaborators(
        client=client,
        remove_members=args.remove_member,
        auto_delete_inactive=args.auto_delete_inactive,
        dry_run=args.dry_run,
    )

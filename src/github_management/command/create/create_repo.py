from ...client import Client
from ..utils import load_repository_creation_config_yaml

def create_repo(client: Client, args) -> None:
    """Create a repository in user account using a template repository."""

    config = load_repository_creation_config_yaml(args.file)

    if args.dry_run:
        # pylint: disable=C0301
        print(f"[create repo] Dry run: Repository '{config.name}' would be created from template '{config.template_repository}'.")
        # pylint: enable=C0301
        return

    config.create(client=client)
    # pylint: disable=C0301
    print(f"[create repo] Repository '{config.name}' created successfully from template '{config.template_repository}'.")
    # pylint: enable=C0301

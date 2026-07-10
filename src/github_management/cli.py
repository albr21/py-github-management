import argparse

def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github-management",
        description="GitHub Management Tool"
    )

    parser.add_argument(
        "-v", "--version",
        action="store_true",
        default=False,
        help="Enable verbose mode",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # =========================================================================
    # Extract
    # =========================================================================
    extract_parser = subparsers.add_parser(
        "extract",
        aliases=["e"],
        help="Extract organization data from GitHub API and save it to a YAML file"
    )

    extract_parser.add_argument(
        "-o", "--orgs",
        nargs="+",
        required=False,
        help="List of organization names to extract data from"
    )

    extract_parser.add_argument(
        "-f", "--file",
        default="./github_management.yaml",
        help="Output YAML file name (default: github_management.yaml)"
    )

    # =========================================================================
    # Diff
    # =========================================================================
    diff_parser = subparsers.add_parser(
        "diff",
        aliases=["d"],
        help="Diff organization data modifications from a YAML file against GitHub API"
    )

    diff_parser.add_argument(
        "-o", "--orgs",
        nargs="+",
        required=True,
        help="List of organization names to diff data from"
    )

    diff_parser.add_argument(
        "-f", "--file",
        default="./github_management.yaml",
        help="Input YAML file name (default: github_management.yaml)"
    )

    # =========================================================================
    # Validate
    # =========================================================================
    validate_parser = subparsers.add_parser(
        "validate",
        aliases=["v"],
        help="Validate organization data modifications from a YAML file against GitHub API"
    )

    validate_parser.add_argument(
        "-f", "--file",
        default="./github_management.yaml",
        help="Input YAML file name (default: github_management.yaml)"
    )

    # =========================================================================
    # Push
    # =========================================================================
    push_parser = subparsers.add_parser(
        "push",
        aliases=["p"],
        help="Push data modifications from a YAML file"
    )

    push_parser.add_argument(
        "-f", "--file",
        default="./github_management.yaml",
        help="Input YAML file name (default: github_management.yaml)"
    )

    push_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simulate changes without applying them",
    )

    push_scope_subparsers = push_parser.add_subparsers(
        dest="push_scope",
        help="What to push (organization or user level)",
        required=True
    )

    # User level push
    push_user_parser = push_scope_subparsers.add_parser(
        "user",
        help="Push user level data (repositories, topics, etc.)"
    )

    push_user_subparsers = push_user_parser.add_subparsers(
        dest="push_target",
        help="What to push",
        required=True
    )

    # User Push topics
    push_user_topics_parser = push_user_subparsers.add_parser(
        "topics",
        help="Push repository topics modifications",
    )

    push_user_topics_parser.add_argument(
        "--repo-filter",
        default=None,
        help="Filter repositories by name/pattern (supports wildcards)",
    )

    # User Cleanup Members
    push_user_cleanup_parser = push_user_subparsers.add_parser(
        "cleanup",
        help="Cleanup user repositories members",
    )
    push_user_cleanup_group = push_user_cleanup_parser.add_mutually_exclusive_group(required=True)
    push_user_cleanup_group.add_argument(
        "--auto-delete-inactive",
        action="store_true",
        help="Auto delete users that no longer exist on GitHub",
    )
    push_user_cleanup_group.add_argument(
        "--remove-member",
        nargs="+",
        help="Remove specific members from the repositories (everywhere)",
    )

    # Org level push
    push_org_parser = push_scope_subparsers.add_parser(
        "org",
        help="Push organization level data (teams, members, topics, etc.)"
    )

    push_org_subparsers = push_org_parser.add_subparsers(
        dest="push_target",
        help="What to push",
        required=True
    )

    # Org Push topics
    push_org_topics_parser = push_org_subparsers.add_parser(
        "topics",
        help="Push repository topics modifications",
    )

    push_org_topics_parser.add_argument(
        "--repo-filter",
        default=None,
        help="Filter repositories by name/pattern (supports wildcards)",
    )

    push_org_topics_parser.add_argument(
        "-o", "--orgs",
        nargs="+",
        required=False,
        help="List of organization names to push topics to, if not specified, \
            topics will be pushed to all organizations in the YAML file",
    )

    # Org Push teams
    push_org_teams_parser = push_org_subparsers.add_parser(
        "teams",
        help="Push teams modifications (members, inheritance, roles, repo roles)",
    )

    push_org_teams_parser.add_argument(
        "--team-filter",
        default=None,
        help="Filter teams by name/pattern (supports wildcards)",
    )

    push_org_teams_parser.add_argument(
        "-o", "--orgs",
        nargs="+",
        required=False,
        help="List of organization names to push teams to, if not specified, \
            teams will be pushed to all organizations in the YAML file",
    )

    # Org Cleanup Members
    push_org_cleanup_parser = push_org_subparsers.add_parser(
        "cleanup",
        help="Cleanup organization members",
    )

    push_org_cleanup_group = push_org_cleanup_parser.add_mutually_exclusive_group(required=True)
    push_org_cleanup_group.add_argument(
        "--auto-delete-inactive",
        action="store_true",
        help="Auto delete users that no longer exist on GitHub",
    )
    push_org_cleanup_group.add_argument(
        "--remove-member",
        nargs="+",
        help="Remove specific members from the organization (everywhere)",
    )

    # =========================================================================
    # Create
    # =========================================================================
    create_parser = subparsers.add_parser(
        "create",
        aliases=["c"],
        help="Create github elements from a YAML configuration file"
    )

    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simulate changes without applying them",
    )

    create_subparsers = create_parser.add_subparsers(
        dest="create_target",
        help="What to create",
        required=True
    )

    # Create repository (User)
    create_repo_parser = create_subparsers.add_parser(
        "repo",
        aliases=["r"],
        help="Create a repository in user account using a template repository"
    )

    create_repo_parser.add_argument(
        "-f", "--file",
        default="./create_repository_config.yaml",
        help="Input YAML file name (default: create_repository_config.yaml)"
    )

    return parser

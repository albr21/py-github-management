import pytest

from github_management.cli import build_cli

class TestCommandCliBuild:
    def test_command_cli_parses_extract_command(self):
        parser = build_cli()
        args = parser.parse_args(["extract"])

        assert args.command == "extract"
        assert args.file == "./github_management.yaml"
        assert args.orgs is None

    def test_command_cli_parses_push_user_topics_command(self):
        parser = build_cli()
        args = parser.parse_args(["push", "user", "topics"])

        assert args.command == "push"
        assert args.push_scope == "user"
        assert args.push_target == "topics"
        assert args.dry_run is False

    def test_command_cli_parses_push_org_cleanup_auto_delete_inactive(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "cleanup", "--auto-delete-inactive"])

        assert args.command == "push"
        assert args.push_scope == "org"
        assert args.push_target == "cleanup"
        assert args.auto_delete_inactive is True
        assert args.remove_member is None

    def test_command_cli_parses_push_org_cleanup_remove_member(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "cleanup", "--remove-member", "alice", "bob"])

        assert args.push_scope == "org"
        assert args.push_target == "cleanup"
        assert args.remove_member == ["alice", "bob"]
        assert args.auto_delete_inactive is False

    def test_command_cli_parses_push_user_cleanup_auto_delete_inactive(self):
        parser = build_cli()
        args = parser.parse_args(["push", "user", "cleanup", "--auto-delete-inactive"])

        assert args.command == "push"
        assert args.push_scope == "user"
        assert args.push_target == "cleanup"
        assert args.auto_delete_inactive is True
        assert args.remove_member is None

    def test_command_cli_parses_push_user_cleanup_remove_member(self):
        parser = build_cli()
        args = parser.parse_args(["push", "user", "cleanup", "--remove-member", "alice"])

        assert args.push_scope == "user"
        assert args.push_target == "cleanup"
        assert args.remove_member == ["alice"]
        assert args.auto_delete_inactive is False

    def test_command_cli_push_org_cleanup_requires_exclusive_group(self):
        parser = build_cli()
        with pytest.raises(SystemExit):
            parser.parse_args(["push", "org", "cleanup"])

    def test_command_cli_parses_push_org_teams_command(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "teams"])

        assert args.command == "push"
        assert args.push_scope == "org"
        assert args.push_target == "teams"
        assert args.team_filter is None
        assert args.orgs is None
        assert args.dry_run is False

    def test_command_cli_parses_push_org_teams_with_filter(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "teams", "--team-filter", "backend-*"])

        assert args.push_target == "teams"
        assert args.team_filter == "backend-*"

    def test_command_cli_parses_push_org_teams_with_org_filter(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "teams", "--orgs", "my-org", "other-org"])

        assert args.push_target == "teams"
        assert args.orgs == ["my-org", "other-org"]

    def test_command_cli_parses_create_repo_command(self):
        parser = build_cli()
        args = parser.parse_args(["create", "repo"])

        assert args.command == "create"
        assert args.create_target == "repo"
        assert args.file == "./create_repository_config.yaml"

    def test_command_cli_parses_create_repo_with_dry_run(self):
        parser = build_cli()
        args = parser.parse_args(["create", "--dry-run", "repo"])

        assert args.create_target == "repo"
        assert args.dry_run is True

    def test_command_cli_parses_create_repo_with_custom_file(self):
        parser = build_cli()
        args = parser.parse_args(["create", "repo", "--file", "/tmp/file.yaml"])

        assert args.create_target == "repo"
        assert args.file == "/tmp/file.yaml"

    def test_command_cli_parses_diff_command(self):
        parser = build_cli()
        args = parser.parse_args(["diff", "--orgs", "OrgA"])

        assert args.command == "diff"
        assert args.orgs == ["OrgA"]
        assert args.file == "./github_management.yaml"

    def test_command_cli_parses_diff_with_custom_file(self):
        parser = build_cli()
        args = parser.parse_args(["diff", "--orgs", "OrgA", "--file", "/tmp/file.yaml"])

        assert args.command == "diff"
        assert args.file == "/tmp/file.yaml"

    def test_command_cli_parses_validate_command(self):
        parser = build_cli()
        args = parser.parse_args(["validate"])

        assert args.command == "validate"
        assert args.file == "./github_management.yaml"

    def test_command_cli_parses_validate_with_custom_file(self):
        parser = build_cli()
        args = parser.parse_args(["validate", "--file", "/tmp/file.yaml"])

        assert args.command == "validate"
        assert args.file == "/tmp/file.yaml"

    def test_command_cli_parses_extract_with_custom_file(self):
        parser = build_cli()
        args = parser.parse_args(["extract", "--file", "/tmp/file.yaml"])

        assert args.command == "extract"
        assert args.file == "/tmp/file.yaml"

    def test_command_cli_parses_extract_with_orgs(self):
        parser = build_cli()
        args = parser.parse_args(["extract", "--orgs", "OrgA", "OrgB"])

        assert args.command == "extract"
        assert args.orgs == ["OrgA", "OrgB"]

    def test_command_cli_parses_push_user_topics_with_repo_filter(self):
        parser = build_cli()
        args = parser.parse_args(["push", "user", "topics", "--repo-filter", "my-repo-*"])

        assert args.push_target == "topics"
        assert args.repo_filter == "my-repo-*"

    def test_command_cli_parses_push_user_topics_with_dry_run(self):
        parser = build_cli()
        args = parser.parse_args(["push", "--dry-run", "user", "topics"])

        assert args.push_target == "topics"
        assert args.dry_run is True

    def test_command_cli_push_user_cleanup_requires_exclusive_group(self):
        parser = build_cli()
        with pytest.raises(SystemExit):
            parser.parse_args(["push", "user", "cleanup"])

    def test_command_cli_parses_push_org_topics_command(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "topics"])

        assert args.command == "push"
        assert args.push_scope == "org"
        assert args.push_target == "topics"
        assert args.repo_filter is None
        assert args.orgs is None

    def test_command_cli_parses_push_org_topics_with_repo_filter(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "topics", "--repo-filter", "my-repo-*"])

        assert args.push_target == "topics"
        assert args.repo_filter == "my-repo-*"

    def test_command_cli_parses_push_org_topics_with_orgs(self):
        parser = build_cli()
        args = parser.parse_args(["push", "org", "topics", "--orgs", "OrgA", "OrgB"])

        assert args.push_target == "topics"
        assert args.orgs == ["OrgA", "OrgB"]

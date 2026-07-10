from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.push.org.teams import push_org_teams

class TestCommandPushOrgTeams:
    def test_command_push_org_teams_calls_push_teams_to_github_for_orgs(self, monkeypatch):
        local = SimpleNamespace(push_teams_to_github_for_orgs=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.teams.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_teams(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", team_filter="team*", orgs=["my-org"], dry_run=False),
        )

        local.push_teams_to_github_for_orgs.assert_called_once_with(
            client=SimpleNamespace(), org_filter=["my-org"], team_filter="team*", dry_run=False
        )

    def test_command_push_org_teams_no_filter_passes_none(self, monkeypatch):
        local = SimpleNamespace(push_teams_to_github_for_orgs=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.teams.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_teams(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", team_filter=None, orgs=None, dry_run=False),
        )

        local.push_teams_to_github_for_orgs.assert_called_once_with(
            client=SimpleNamespace(), org_filter=None, team_filter=None, dry_run=False
        )

    def test_command_push_org_teams_reports_dry_run(self, monkeypatch, capsys):
        local = SimpleNamespace(push_teams_to_github_for_orgs=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.teams.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_teams(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", team_filter=None, orgs=None, dry_run=True),
        )

        assert "DRY RUN" in capsys.readouterr().out

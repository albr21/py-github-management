from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.diff import diff

class TestCommandDiff:
    def test_command_diff_calls_fetch_and_prints_changes(self, monkeypatch, capsys):
        local = SimpleNamespace(diff=Mock(return_value="changes"))
        remote = object()

        monkeypatch.setattr(
            "github_management.command.diff.load_github_management_yaml",
            Mock(return_value=local),
        )
        monkeypatch.setattr(
            "github_management.command.diff.GitHubManagement.fetch_from_github",
            Mock(return_value=remote),
        )

        diff(SimpleNamespace(), SimpleNamespace(file="/tmp/file.yaml", orgs=["OrgA"]))

        assert "changes" in capsys.readouterr().out

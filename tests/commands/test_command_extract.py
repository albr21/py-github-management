from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.extract import extract

class TestCommandExtract:
    def test_command_extract_saves_yaml(self, monkeypatch, capsys):
        local = SimpleNamespace(to_yaml=Mock(return_value="yaml-output"))

        monkeypatch.setattr(
            "github_management.command.extract.GitHubManagement.fetch_from_github",
            Mock(return_value=local),
        )
        save_mock = Mock()
        monkeypatch.setattr("github_management.command.extract.save", save_mock)

        extract(SimpleNamespace(), SimpleNamespace(file="/tmp/out.yaml", orgs=["OrgA"]))

        save_mock.assert_called_once_with("/tmp/out.yaml", "yaml-output")
        assert "Data extracted" in capsys.readouterr().out

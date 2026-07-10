from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.create.create_repo import create_repo

class TestCommandCreateRepo:
    def test_command_create_repo_dry_run_skips_create(self, monkeypatch, capsys):
        config = SimpleNamespace(template_repository="org/template", name="repo1", create=Mock())
        monkeypatch.setattr(
            "github_management.command.create.create_repo.load_repository_creation_config_yaml",
            Mock(return_value=config),
        )

        create_repo(SimpleNamespace(), SimpleNamespace(file="/tmp/create.yaml", dry_run=True))

        config.create.assert_not_called()
        assert "Dry run" in capsys.readouterr().out

    def test_command_create_repo_calls_create_when_not_dry_run(self, monkeypatch, capsys):
        config = SimpleNamespace(template_repository="org/template", name="repo1", create=Mock())
        monkeypatch.setattr(
            "github_management.command.create.create_repo.load_repository_creation_config_yaml",
            Mock(return_value=config),
        )

        create_repo(SimpleNamespace(), SimpleNamespace(file="/tmp/create.yaml", dry_run=False))

        config.create.assert_called_once()
        assert "created successfully" in capsys.readouterr().out

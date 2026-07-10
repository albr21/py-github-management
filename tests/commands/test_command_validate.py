from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.validate import validate

class TestCommandValidate:
    def test_command_validate_success(self, tmp_path, capsys):
        yml = tmp_path / "file.yaml"
        yml.write_text("user:\n  name: test\n  repositories: []\norganizations: []\n")

        validate(SimpleNamespace(file=str(yml)))

        assert "is valid" in capsys.readouterr().out

    def test_command_validate_error_is_reported(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "github_management.command.validate.load_github_management_yaml",
            Mock(side_effect=RuntimeError("bad yaml")),
        )

        validate(SimpleNamespace(file="/tmp/file.yaml"))

        assert "Error validating file" in capsys.readouterr().out

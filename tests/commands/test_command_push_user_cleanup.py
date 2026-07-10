from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.push.user.cleanup import push_user_cleanup

class TestCommandPushUserCleanup:
    def test_command_push_user_cleanup_calls_cleanup_user_collaborators_auto_delete(self, monkeypatch):
        local = SimpleNamespace(cleanup_user_collaborators=Mock())
        monkeypatch.setattr(
            "github_management.command.push.user.cleanup.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_user_cleanup(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", auto_delete_inactive=True, remove_member=None, dry_run=False),
        )

        local.cleanup_user_collaborators.assert_called_once_with(
            client=SimpleNamespace(),
            remove_members=None,
            auto_delete_inactive=True,
            dry_run=False,
        )

    def test_command_push_user_cleanup_calls_cleanup_user_collaborators_remove_member(self, monkeypatch):
        local = SimpleNamespace(cleanup_user_collaborators=Mock())
        monkeypatch.setattr(
            "github_management.command.push.user.cleanup.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_user_cleanup(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", auto_delete_inactive=False, remove_member=["alice"], dry_run=False),
        )

        local.cleanup_user_collaborators.assert_called_once_with(
            client=SimpleNamespace(),
            remove_members=["alice"],
            auto_delete_inactive=False,
            dry_run=False,
        )

    def test_command_push_user_cleanup_reports_dry_run(self, monkeypatch, capsys):
        local = SimpleNamespace(cleanup_user_collaborators=Mock())
        monkeypatch.setattr(
            "github_management.command.push.user.cleanup.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_user_cleanup(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", auto_delete_inactive=False, remove_member=["alice"], dry_run=True),
        )

        assert "DRY RUN" in capsys.readouterr().out
        local.cleanup_user_collaborators.assert_called_once_with(
            client=SimpleNamespace(),
            remove_members=["alice"],
            auto_delete_inactive=False,
            dry_run=True,
        )

from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.push.org.cleanup import push_org_cleanup

class TestCommandPushOrgCleanup:
    def test_command_push_org_cleanup_calls_cleanup_org_members_auto_delete(self, monkeypatch):
        local = SimpleNamespace(cleanup_org_members=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.cleanup.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_cleanup(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", auto_delete_inactive=True, remove_member=None, dry_run=False),
        )

        local.cleanup_org_members.assert_called_once_with(
            client=SimpleNamespace(),
            remove_members=None,
            auto_delete_inactive=True,
            dry_run=False,
        )

    def test_command_push_org_cleanup_calls_cleanup_org_members_remove_member(self, monkeypatch):
        local = SimpleNamespace(cleanup_org_members=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.cleanup.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_cleanup(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", auto_delete_inactive=False, remove_member=["alice", "bob"], dry_run=False),
        )

        local.cleanup_org_members.assert_called_once_with(
            client=SimpleNamespace(),
            remove_members=["alice", "bob"],
            auto_delete_inactive=False,
            dry_run=False,
        )

    def test_command_push_org_cleanup_reports_dry_run(self, monkeypatch, capsys):
        local = SimpleNamespace(cleanup_org_members=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.cleanup.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_cleanup(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", auto_delete_inactive=True, remove_member=None, dry_run=True),
        )

        assert "DRY RUN" in capsys.readouterr().out
        local.cleanup_org_members.assert_called_once_with(
            client=SimpleNamespace(),
            remove_members=None,
            auto_delete_inactive=True,
            dry_run=True,
        )

from types import SimpleNamespace
from unittest.mock import Mock

from github_management.command.push.org.topics import push_org_topics
from github_management.command.push.user.topics import push_user_topics

class TestCommandPushOrgTopics:
    def test_command_push_org_topics_calls_organization_push(self, monkeypatch):
        local = SimpleNamespace(push_repositories_to_github_for_orgs=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.topics.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_topics(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", orgs=["OrgA"], repo_filter="repo*", dry_run=False),
        )

        local.push_repositories_to_github_for_orgs.assert_called_once_with(
            client=SimpleNamespace(), org_filter=["OrgA"], repo_filter="repo*", fields={"topics"}, dry_run=False
        )

    def test_command_push_org_topics_reports_dry_run(self, monkeypatch, capsys):
        local = SimpleNamespace(push_repositories_to_github_for_orgs=Mock())
        monkeypatch.setattr(
            "github_management.command.push.org.topics.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_org_topics(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", orgs=None, repo_filter=None, dry_run=True),
        )

        assert "DRY RUN" in capsys.readouterr().out

class TestCommandPushUserTopics:
    def test_command_push_user_topics_calls_user_push(self, monkeypatch):
        local = SimpleNamespace(push_repositories_to_github_for_user=Mock())
        monkeypatch.setattr(
            "github_management.command.push.user.topics.load_github_management_yaml",
            Mock(return_value=local),
        )

        push_user_topics(
            SimpleNamespace(),
            SimpleNamespace(file="/tmp/file.yaml", repo_filter="repo*", dry_run=True),
        )

        local.push_repositories_to_github_for_user.assert_called_once_with(
            client=SimpleNamespace(), repo_filter="repo*", fields={"topics"}, dry_run=True
        )

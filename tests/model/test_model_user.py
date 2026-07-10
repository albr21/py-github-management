from types import SimpleNamespace
from unittest.mock import Mock

from github_management.model.github.repository import Repository
from github_management.model.github.user import User

class TestModelUserFetchFromGitHub:
    def test_model_user_fetch_from_github(self, monkeypatch):
        class FakeGithubUser:
            login = "octocat"

            def get_repos(self, affiliation):
                return [SimpleNamespace(name="repo1"), SimpleNamespace(name="repo2")]

        class FakeClient:
            client = SimpleNamespace(get_user=lambda: FakeGithubUser())

        monkeypatch.setattr(
            Repository,
            "from_github_object",
            classmethod(lambda cls, github_object: Repository(name=github_object.name, owner="octocat")),
        )

        user = User.fetch_from_github(client=FakeClient())

        assert user.name == "octocat"
        assert [repo.name for repo in user.repositories] == ["repo1", "repo2"]

class TestModelUserPushRepositories:
    def test_model_user_push_repositories_respects_filter(self):
        class FakeRepository:
            def __init__(self, name):
                self.name = name
                self.calls = []

            def push_to_github(self, **kwargs):
                self.calls.append(kwargs)

        repo_keep = FakeRepository("keep")
        repo_skip = FakeRepository("skip")
        user = User(name="octocat", repositories=[repo_keep, repo_skip])

        user.push_repositories_to_github(client=object(), repo_filter=["keep"], fields={"description"}, dry_run=True)

        assert len(repo_keep.calls) == 1
        assert repo_skip.calls == []

class TestModelUserCleanupCollaborators:
    def test_model_user_cleanup_collaborators_delegates_to_each_repo(self):
        repo1 = SimpleNamespace(cleanup_collaborators=Mock())
        repo2 = SimpleNamespace(cleanup_collaborators=Mock())
        user = User(name="alice", repositories=[repo1, repo2])
        client = SimpleNamespace()

        user.cleanup_collaborators(client=client, remove_members=["bob"], auto_delete_inactive=False, dry_run=True)

        repo1.cleanup_collaborators.assert_called_once_with(
            client=client, remove_members=["bob"], auto_delete_inactive=False, dry_run=True
        )
        repo2.cleanup_collaborators.assert_called_once_with(
            client=client, remove_members=["bob"], auto_delete_inactive=False, dry_run=True
        )

    def test_model_user_cleanup_collaborators_empty_repositories_does_nothing(self):
        user = User(name="alice", repositories=[])
        user.cleanup_collaborators(client=SimpleNamespace(), auto_delete_inactive=True, dry_run=False)

class TestModelUserDiff:
    def test_model_user_diff_detects_name_change(self):
        local = User(name="alice", repositories=[])
        remote = User(name="alice-renamed", repositories=[])

        changes = local.diff(remote, path="user")

        assert len(changes) == 1
        assert changes[0].path == "user.name"

    def test_model_user_diff_returns_empty_when_equal(self):
        local = User(name="alice", repositories=[])
        remote = User(name="alice", repositories=[])

        assert local.diff(remote) == []

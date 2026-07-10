import pytest
from types import SimpleNamespace
from unittest.mock import Mock

from github.GithubException import UnknownObjectException

from github_management.model.github.repository import Repository
from github_management.model.github.repository_permissions import RepositoryPermissions
from github_management.model.github.repository_visibility import RepositoryVisibility

class TestModelRepositoryFromGitHubObject:
    @pytest.mark.parametrize(
        ("visibility_value", "expected_visibility"),
        [
            ("public", RepositoryVisibility.PUBLIC),
            ("private", RepositoryVisibility.PRIVATE),
            ("internal", RepositoryVisibility.INTERNAL),
            ("something-else", RepositoryVisibility.UNKNOWN),
        ],
    )
    def test_model_repository_from_github_object_maps_visibility(self, monkeypatch, visibility_value, expected_visibility):
        sentinel_permissions = RepositoryPermissions(admin=["alice"], maintain=[], write=[], triage=[], read=[])

        class FakeOwner:
            login = "org"

        class FakeRepository:
            name = "repo1"
            owner = FakeOwner()
            description = "desc"
            archived = True
            visibility = visibility_value

            def get_topics(self):
                return ["python", "ml"]

        monkeypatch.setattr(
            RepositoryPermissions,
            "from_github_object",
            classmethod(lambda cls, github_object: sentinel_permissions),
        )

        repository = Repository.from_github_object(FakeRepository())

        assert repository.name == "repo1"
        assert repository.owner == "org"
        assert repository.description == "desc"
        assert repository.archive is True
        assert repository.visibility == expected_visibility
        assert repository.topics == ["python", "ml"]
        assert repository.permissions is sentinel_permissions

class TestModelRepositoryPushToGitHub:
    def test_model_repository_push_to_github_edits_and_replaces_topics(self):
        class FakeGithubRepo:
            def __init__(self):
                self.edits = []
                self.replaced_topics = []

            def edit(self, **kwargs):
                self.edits.append(kwargs)

            def replace_topics(self, topics):
                self.replaced_topics.append(topics)

        fake_github_repo = FakeGithubRepo()

        class FakeClient:
            client = SimpleNamespace(get_repo=lambda name: fake_github_repo)

        repository = Repository(name="repo1", owner="org", description="new desc", topics=["python"])

        repository.push_to_github(client=FakeClient(), fields=None, dry_run=False)

        assert fake_github_repo.edits == [{"description": "new desc"}]
        assert fake_github_repo.replaced_topics == [["python"]]

    def test_model_repository_push_to_github_dry_run_skips_api_calls(self, capsys):
        class FakeGithubRepo:
            def edit(self, **kwargs):
                raise AssertionError("edit should not be called")

            def replace_topics(self, topics):
                raise AssertionError("replace_topics should not be called")

        class FakeClient:
            client = SimpleNamespace(get_repo=lambda name: FakeGithubRepo())

        repository = Repository(name="repo1", owner="org", description="new desc", topics=["python"])

        repository.push_to_github(client=FakeClient(), fields={"description", "topics"}, dry_run=True)

        assert "DRY RUN" in capsys.readouterr().out

class TestModelRepositoryCleanupCollaborators:
    def test_model_repository_cleanup_collaborators_no_permissions_returns_early(self):
        repo = Repository(name="repo1", owner="org", permissions=None)
        client = SimpleNamespace(client=SimpleNamespace(get_repo=Mock()))
        repo.cleanup_collaborators(client=client, auto_delete_inactive=True, dry_run=False)
        client.client.get_repo.assert_not_called()

    def test_model_repository_cleanup_collaborators_auto_delete_inactive_removes_missing_user(self, capsys):
        github_repo = SimpleNamespace(
            url="https://api.github.test/repos/org/repo1",
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
            remove_from_collaborators=Mock(),
        )
        client = SimpleNamespace(
            client=SimpleNamespace(
                get_user=Mock(side_effect=UnknownObjectException(status=404, data={})),
                get_repo=lambda name: github_repo,
            )
        )
        perms = RepositoryPermissions(admin=["ghost"], maintain=[], write=[], triage=[], read=[])
        repo = Repository(name="repo1", owner="org", permissions=perms)

        repo.cleanup_collaborators(client=client, auto_delete_inactive=True, dry_run=False)

        github_repo._requester.requestJsonAndCheck.assert_called_once()
        assert "ghost" in capsys.readouterr().out

    def test_model_repository_cleanup_collaborators_auto_delete_dry_run_skips_api_call(self, capsys):
        github_repo = SimpleNamespace(
            url="https://api.github.test/repos/org/repo1",
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        client = SimpleNamespace(
            client=SimpleNamespace(
                get_user=Mock(side_effect=UnknownObjectException(status=404, data={})),
                get_repo=lambda name: github_repo,
            )
        )
        perms = RepositoryPermissions(admin=["ghost"], maintain=[], write=[], triage=[], read=[])
        repo = Repository(name="repo1", owner="org", permissions=perms)

        repo.cleanup_collaborators(client=client, auto_delete_inactive=True, dry_run=True)

        github_repo._requester.requestJsonAndCheck.assert_not_called()

    def test_model_repository_cleanup_collaborators_remove_member_calls_api(self, capsys):
        removed = []
        github_repo = SimpleNamespace(
            url="https://api.github.test/repos/org/repo1",
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
            remove_from_collaborators=lambda user: removed.append(user.login),
        )
        client = SimpleNamespace(
            client=SimpleNamespace(
                get_user=lambda login: SimpleNamespace(login=login),
                get_repo=lambda name: github_repo,
            )
        )
        perms = RepositoryPermissions(admin=[], maintain=[], write=["alice"], triage=[], read=[])
        repo = Repository(name="repo1", owner="org", permissions=perms)

        repo.cleanup_collaborators(client=client, remove_members=["alice"], dry_run=False)

        assert "alice" in removed

    def test_model_repository_cleanup_collaborators_remove_member_not_in_permissions_is_skipped(self):
        github_repo = SimpleNamespace(
            url="https://api.github.test/repos/org/repo1",
            remove_from_collaborators=Mock(),
        )
        client = SimpleNamespace(
            client=SimpleNamespace(
                get_user=lambda login: SimpleNamespace(login=login),
                get_repo=lambda name: github_repo,
            )
        )
        perms = RepositoryPermissions(admin=[], maintain=[], write=[], triage=[], read=[])
        repo = Repository(name="repo1", owner="org", permissions=perms)

        repo.cleanup_collaborators(client=client, remove_members=["unknown"], dry_run=False)

        github_repo.remove_from_collaborators.assert_not_called()

    def test_model_repository_cleanup_collaborators_remove_member_unknown_on_github_prints_warning(self, capsys):
        github_repo = SimpleNamespace(
            url="https://api.github.test/repos/org/repo1",
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
            remove_from_collaborators=Mock(),
        )
        client = SimpleNamespace(
            client=SimpleNamespace(
                get_user=Mock(side_effect=UnknownObjectException(status=404, data={})),
                get_repo=lambda name: github_repo,
            )
        )
        perms = RepositoryPermissions(admin=["ghost"], maintain=[], write=[], triage=[], read=[])
        repo = Repository(name="repo1", owner="org", permissions=perms)

        repo.cleanup_collaborators(client=client, remove_members=["ghost"], dry_run=False)

        github_repo.remove_from_collaborators.assert_not_called()
        assert "Warning" in capsys.readouterr().out

class TestModelRepositoryFromDict:
    def test_model_repository_from_dict_defaults_to_unknown_visibility_when_absent(self):
        repo = Repository.from_dict({"name": "repo1", "owner": "org"})

        assert repo.visibility == RepositoryVisibility.UNKNOWN

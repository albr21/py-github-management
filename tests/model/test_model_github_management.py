from types import SimpleNamespace
from unittest.mock import Mock

from github_management.model.github.github_management import GitHubManagement
from github_management.model.github.organization import Organization
from github_management.model.github.user import User

class TestModelGitHubManagementFetchFromGitHub:
    def test_model_github_management_fetch_from_github_without_orgs(self, monkeypatch):
        monkeypatch.setattr(User, "fetch_from_github", classmethod(lambda cls, client: User(name="octocat")))

        management = GitHubManagement.fetch_from_github(client=object(), organization_names=[])

        assert management.user.name == "octocat"
        assert management.organizations == []

    def test_model_github_management_fetch_from_github_with_orgs(self, monkeypatch):
        monkeypatch.setattr(User, "fetch_from_github", classmethod(lambda cls, client: User(name="octocat")))
        monkeypatch.setattr(
            Organization,
            "fetch_from_github",
            classmethod(lambda cls, client, name: Organization(name=name, description="", members=[], teams=[], repositories=[], roles=[])),
        )

        management = GitHubManagement.fetch_from_github(client=object(), organization_names=["OrgA", "OrgB"])

        assert [org.name for org in management.organizations] == ["OrgA", "OrgB"]

class TestModelGitHubManagementPushMethods:
    def test_model_github_management_push_methods(self):
        class FakeOrg:
            def __init__(self, name):
                self.name = name
                self.calls = []

            def push_repositories_to_github(self, **kwargs):
                self.calls.append(kwargs)

        class FakeUser:
            def __init__(self):
                self.calls = []

            def push_repositories_to_github(self, **kwargs):
                self.calls.append(kwargs)

        keep = FakeOrg("keep")
        skip = FakeOrg("skip")
        user = FakeUser()
        management = GitHubManagement(user=user, organizations=[keep, skip])

        management.push_repositories_to_github_for_orgs(
            client=object(),
            org_filter=["keep"],
            repo_filter=["repo"],
            fields={"description"},
            dry_run=True,
        )
        management.push_repositories_to_github_for_user(client=object(), repo_filter=["repo"], fields=None, dry_run=False)

        assert len(keep.calls) == 1
        assert skip.calls == []
        assert len(user.calls) == 1

class TestModelGitHubManagementCleanup:
    def test_model_cleanup_org_members_delegates_to_each_org(self):
        org1 = SimpleNamespace(name="OrgA", cleanup_members=Mock())
        org2 = SimpleNamespace(name="OrgB", cleanup_members=Mock())
        gm = GitHubManagement(user=SimpleNamespace(), organizations=[org1, org2])
        client = SimpleNamespace()

        gm.cleanup_org_members(client=client, remove_members=["alice"], auto_delete_inactive=False, dry_run=True)

        org1.cleanup_members.assert_called_once_with(
            client=client, remove_members=["alice"], auto_delete_inactive=False, dry_run=True
        )
        org2.cleanup_members.assert_called_once_with(
            client=client, remove_members=["alice"], auto_delete_inactive=False, dry_run=True
        )

    def test_model_cleanup_user_collaborators_delegates_to_user(self):
        user = SimpleNamespace(cleanup_collaborators=Mock())
        gm = GitHubManagement(user=user, organizations=[])
        client = SimpleNamespace()

        gm.cleanup_user_collaborators(client=client, remove_members=None, auto_delete_inactive=True, dry_run=False)

        user.cleanup_collaborators.assert_called_once_with(
            client=client, remove_members=None, auto_delete_inactive=True, dry_run=False
        )

class TestModelGitHubManagementPushTeams:
    def test_model_push_teams_delegates_to_each_org(self):
        org1 = SimpleNamespace(name="OrgA", push_teams_to_github=Mock())
        org2 = SimpleNamespace(name="OrgB", push_teams_to_github=Mock())
        gm = GitHubManagement(user=SimpleNamespace(), organizations=[org1, org2])
        client = SimpleNamespace()

        gm.push_teams_to_github_for_orgs(client=client, org_filter=None, team_filter="backend-*", dry_run=True)

        org1.push_teams_to_github.assert_called_once_with(client=client, team_filter="backend-*", dry_run=True)
        org2.push_teams_to_github.assert_called_once_with(client=client, team_filter="backend-*", dry_run=True)

    def test_model_push_teams_no_filter_passes_none(self):
        org = SimpleNamespace(name="OrgA", push_teams_to_github=Mock())
        gm = GitHubManagement(user=SimpleNamespace(), organizations=[org])

        gm.push_teams_to_github_for_orgs(client=SimpleNamespace(), org_filter=None, team_filter=None, dry_run=False)

        org.push_teams_to_github.assert_called_once_with(client=SimpleNamespace(), team_filter=None, dry_run=False)

    def test_model_push_teams_org_filter_skips_excluded_orgs(self):
        org1 = SimpleNamespace(name="OrgA", push_teams_to_github=Mock())
        org2 = SimpleNamespace(name="OrgB", push_teams_to_github=Mock())
        gm = GitHubManagement(user=SimpleNamespace(), organizations=[org1, org2])

        gm.push_teams_to_github_for_orgs(client=SimpleNamespace(), org_filter=["OrgA"], team_filter=None, dry_run=False)

        org1.push_teams_to_github.assert_called_once()
        org2.push_teams_to_github.assert_not_called()

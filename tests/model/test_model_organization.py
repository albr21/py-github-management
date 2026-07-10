from types import SimpleNamespace
from unittest.mock import Mock

from github.GithubException import UnknownObjectException

from github_management.model.github.member import Member
from github_management.model.github.organization import Organization
from github_management.model.github.repository import Repository
from github_management.model.github.role import Role
from github_management.model.github.team import Team

class TestModelOrganizationFetchFromGitHub:
    def test_model_organization_fetch_from_github(self, monkeypatch):
        class FakeGithubOrganization:
            description = "org desc"

            def get_members(self):
                return [SimpleNamespace(login="alice", name="Alice")]

            def get_repos(self):
                return [SimpleNamespace(name="repo1")]

        class FakeClient:
            client = SimpleNamespace(get_organization=lambda name: FakeGithubOrganization())

        monkeypatch.setattr(
            Member,
            "from_github_object",
            classmethod(lambda cls, github_object: Member(login=github_object.login, name=github_object.name)),
        )
        monkeypatch.setattr(
            Repository,
            "from_github_object",
            classmethod(lambda cls, github_object: Repository(name=github_object.name, owner="org")),
        )
        monkeypatch.setattr(
            Organization,
            "_Organization__fetch_roles_from_github",
            classmethod(lambda cls, client, organization_name: [Role(name="custom", description="", permissions=[])]),
        )
        monkeypatch.setattr(
            Organization,
            "_fetch_teams_from_github",
            classmethod(lambda cls, github_organization: [Team(name="team1", description="", members=[], parent=None, repositories=[])]),
        )

        organization = Organization.fetch_from_github(client=FakeClient(), name="OrgA")

        assert organization.name == "OrgA"
        assert organization.description == "org desc"
        assert organization.members[0].login == "alice"
        assert organization.repositories[0].name == "repo1"
        assert organization.roles[0].name == "custom"
        assert organization.teams[0].name == "team1"

class TestModelOrganizationFetchRolesFromGitHub:
    def test_model_organization_fetch_roles_from_github(self):
        class FakeRequester:
            def requestJsonAndCheck(self, method, url, headers):
                return None, {
                    "custom_roles": [
                        {"name": "custom", "description": "custom desc", "permissions": ["perm1"]}
                    ]
                }

        class FakeOrganization:
            url = "https://api.github.test/orgs/OrgA"
            _requester = FakeRequester()

        class FakeClient:
            client = SimpleNamespace(get_organization=lambda name: FakeOrganization())

        roles = Organization._Organization__fetch_roles_from_github(FakeClient(), "OrgA")

        assert len(roles) == 6
        assert roles[-1].name == "custom"

class TestModelOrganizationFetchTeamsFromGitHub:
    def test_model_organization_fetch_teams_from_github(self):
        class FakeRequester:
            def requestJsonAndCheck(self, method, url, headers):
                return None, [{"name": "repo1", "role_name": "admin"}]

        class FakeTeam:
            name = "team1"
            description = "team desc"
            parent = None
            url = "https://api.github.test/teams/1"
            _requester = FakeRequester()

            def get_members(self):
                return [SimpleNamespace(login="alice"), SimpleNamespace(login="bob")]

        teams = Organization._fetch_teams_from_github(SimpleNamespace(get_teams=lambda: [FakeTeam()]))

        assert len(teams) == 1
        assert teams[0].name == "team1"
        assert teams[0].members == ["alice", "bob"]
        assert teams[0].repositories[0].name == "repo1"
        assert teams[0].repositories[0].role == "admin"

class TestModelOrganizationPushTeamsToGitHub:
    def _make_github_team(self, *, name, members=None):
        return SimpleNamespace(
            name=name,
            id=1,
            description="",
            parent=None,
            url=f"https://api.github.test/teams/{name}",
            get_members=lambda: [SimpleNamespace(login=m) for m in (members or [])],
            add_to_members=Mock(),
            remove_from_members=Mock(),
            edit=Mock(),
            delete=Mock(),
            _requester=SimpleNamespace(requestJsonAndCheck=Mock(return_value=(None, []))),
        )

    def test_model_organization_push_teams_syncs_existing_team(self, capsys):
        existing = self._make_github_team(name="backend")
        github_org = SimpleNamespace(login="OrgA", get_teams=Mock(return_value=[existing]), create_team=Mock())
        client = SimpleNamespace(client=SimpleNamespace(get_organization=lambda name: github_org, get_user=Mock()))
        local_team = Mock()
        local_team.name = "backend"
        local_team.parent = None
        org = Organization(name="OrgA", teams=[local_team], members=[], repositories=[], roles=[])

        org.push_teams_to_github(client=client)

        local_team.push_to_github.assert_called_once()
        assert "Syncing team 'backend'" in capsys.readouterr().out

    def test_model_organization_push_teams_creates_new_team(self, capsys):
        created = SimpleNamespace(
            id=99, url="https://api.github.test/teams/99",
            add_to_members=Mock(), _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        github_org = SimpleNamespace(login="OrgA", get_teams=Mock(return_value=[]), create_team=Mock(return_value=created))
        client = SimpleNamespace(client=SimpleNamespace(get_organization=lambda name: github_org, get_user=Mock()))
        org = Organization(name="OrgA", teams=[Team(name="new-team", members=[], repositories=[])], members=[], repositories=[], roles=[])

        org.push_teams_to_github(client=client)

        github_org.create_team.assert_called_once()
        assert "new-team" in capsys.readouterr().out

    def test_model_organization_push_teams_deletes_removed_team(self, capsys):
        stale = self._make_github_team(name="stale-team")
        github_org = SimpleNamespace(login="OrgA", get_teams=Mock(return_value=[stale]), create_team=Mock())
        client = SimpleNamespace(client=SimpleNamespace(get_organization=lambda name: github_org, get_user=Mock()))
        org = Organization(name="OrgA", teams=[], members=[], repositories=[], roles=[])

        org.push_teams_to_github(client=client)

        stale.delete.assert_called_once()
        assert "stale-team" in capsys.readouterr().out

    def test_model_organization_push_teams_filter_limits_scope(self, capsys):
        kept = self._make_github_team(name="backend-api")
        ignored = self._make_github_team(name="frontend-ui")
        github_org = SimpleNamespace(login="OrgA", get_teams=Mock(return_value=[kept, ignored]), create_team=Mock())
        client = SimpleNamespace(client=SimpleNamespace(get_organization=lambda name: github_org, get_user=Mock()))
        org = Organization(name="OrgA", teams=[], members=[], repositories=[], roles=[])

        org.push_teams_to_github(client=client, team_filter="backend-*")

        kept.delete.assert_called_once()
        ignored.delete.assert_not_called()

    def test_model_organization_push_teams_dry_run_skips_delete(self, capsys):
        stale = self._make_github_team(name="stale-team")
        github_org = SimpleNamespace(login="OrgA", get_teams=Mock(return_value=[stale]), create_team=Mock())
        client = SimpleNamespace(client=SimpleNamespace(get_organization=lambda name: github_org))
        org = Organization(name="OrgA", teams=[], members=[], repositories=[], roles=[])

        org.push_teams_to_github(client=client, dry_run=True)

        stale.delete.assert_not_called()

class TestModelOrganizationFetchRolesError:
    def test_model_organization_fetch_roles_returns_empty_list_on_api_error(self, capsys):
        class FakeRequester:
            def requestJsonAndCheck(self, method, url, headers):
                raise Exception("API error")

        class FakeOrganization:
            url = "https://api.github.test/orgs/OrgA"
            _requester = FakeRequester()

        class FakeClient:
            client = SimpleNamespace(get_organization=lambda name: FakeOrganization())

        roles = Organization._Organization__fetch_roles_from_github(FakeClient(), "OrgA")

        assert roles == []
        assert "Error fetching roles" in capsys.readouterr().out

class TestModelOrganizationPushRepositories:
    def test_model_organization_push_repositories_calls_each_repo(self):
        repo1 = SimpleNamespace(name="repo1", push_to_github=Mock())
        repo2 = SimpleNamespace(name="repo2", push_to_github=Mock())
        client = SimpleNamespace()
        org = Organization(name="OrgA", members=[], repositories=[repo1, repo2], teams=[], roles=[])

        org.push_repositories_to_github(client=client, fields={"description"}, dry_run=True)

        repo1.push_to_github.assert_called_once_with(client=client, fields={"description"}, dry_run=True)
        repo2.push_to_github.assert_called_once()

    def test_model_organization_push_repositories_respects_filter(self):
        repo_keep = SimpleNamespace(name="keep", push_to_github=Mock())
        repo_skip = SimpleNamespace(name="skip", push_to_github=Mock())
        org = Organization(name="OrgA", members=[], repositories=[repo_keep, repo_skip], teams=[], roles=[])

        org.push_repositories_to_github(client=SimpleNamespace(), repo_filter=["keep"])

        repo_keep.push_to_github.assert_called_once()
        repo_skip.push_to_github.assert_not_called()

class TestModelOrganizationCleanupMembers:
    def test_model_organization_cleanup_members_auto_delete_removes_missing_user(self, capsys):
        github_org = SimpleNamespace(
            url="https://api.github.test/orgs/OrgA",
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        client = SimpleNamespace(client=SimpleNamespace(
            get_organization=lambda name: github_org,
            get_user=Mock(side_effect=UnknownObjectException(status=404, data={})),
        ))
        org = Organization(name="OrgA", members=[Member(login="ghost", name="Ghost")], repositories=[], teams=[], roles=[])

        org.cleanup_members(client=client, auto_delete_inactive=True, dry_run=False)

        github_org._requester.requestJsonAndCheck.assert_called_once()
        assert "ghost" in capsys.readouterr().out

    def test_model_organization_cleanup_members_auto_delete_dry_run_skips_api_call(self, capsys):
        github_org = SimpleNamespace(
            url="https://api.github.test/orgs/OrgA",
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        client = SimpleNamespace(client=SimpleNamespace(
            get_organization=lambda name: github_org,
            get_user=Mock(side_effect=UnknownObjectException(status=404, data={})),
        ))
        org = Organization(name="OrgA", members=[Member(login="ghost", name="Ghost")], repositories=[], teams=[], roles=[])

        org.cleanup_members(client=client, auto_delete_inactive=True, dry_run=True)

        github_org._requester.requestJsonAndCheck.assert_not_called()

    def test_model_organization_cleanup_members_remove_member_calls_api(self, capsys):
        removed = []
        github_org = SimpleNamespace(
            url="https://api.github.test/orgs/OrgA",
            remove_from_members=lambda user: removed.append(user.login),
        )
        client = SimpleNamespace(client=SimpleNamespace(
            get_organization=lambda name: github_org,
            get_user=lambda login: SimpleNamespace(login=login),
        ))
        org = Organization(name="OrgA", members=[], repositories=[], teams=[], roles=[])

        org.cleanup_members(client=client, remove_members=["alice"], dry_run=False)

        assert "alice" in removed

    def test_model_organization_cleanup_members_remove_member_unknown_user_prints_warning(self, capsys):
        github_org = SimpleNamespace(
            url="https://api.github.test/orgs/OrgA",
            remove_from_members=Mock(),
        )
        client = SimpleNamespace(client=SimpleNamespace(
            get_organization=lambda name: github_org,
            get_user=Mock(side_effect=UnknownObjectException(status=404, data={})),
        ))
        org = Organization(name="OrgA", members=[], repositories=[], teams=[], roles=[])

        org.cleanup_members(client=client, remove_members=["ghost"], dry_run=False)

        github_org.remove_from_members.assert_not_called()
        assert "Warning" in capsys.readouterr().out

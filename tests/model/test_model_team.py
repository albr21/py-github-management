from types import SimpleNamespace
from unittest.mock import Mock, call

from github_management.model.github.team import Team
from github_management.model.github.team_repository import TeamRepository

def _make_github_team(*, description="", parent=None, members=None, repos=None):
    """Build a minimal fake PyGithub Team object."""
    members = members or []
    repos = repos or []
    return SimpleNamespace(
        description=description,
        parent=parent,
        id=42,
        url="https://api.github.test/teams/42",
        get_members=lambda: [SimpleNamespace(login=m) for m in members],
        add_to_members=Mock(),
        remove_from_members=Mock(),
        edit=Mock(),
        delete=Mock(),
        _requester=SimpleNamespace(
            requestJsonAndCheck=Mock(return_value=(None, [{"name": r["name"], "role_name": r["role"]} for r in repos]))
        ),
    )

def _make_client(*, users=None):
    users = users or {}
    return SimpleNamespace(
        client=SimpleNamespace(
            get_user=lambda login: SimpleNamespace(login=login),
        )
    )

def _make_github_org(*, login="OrgA", teams=None):
    teams = teams or []
    return SimpleNamespace(login=login, get_teams=lambda: teams)

class TestModelTeamPushToGitHubMembers:
    def test_model_team_push_to_github_adds_new_member(self, capsys):
        github_team = _make_github_team(members=[])
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", members=["alice"], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team.add_to_members.assert_called_once()
        assert "alice" in capsys.readouterr().out

    def test_model_team_push_to_github_removes_old_member(self, capsys):
        github_team = _make_github_team(members=["bob"])
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", members=[], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team.remove_from_members.assert_called_once()
        assert "bob" in capsys.readouterr().out

    def test_model_team_push_to_github_dry_run_skips_member_api_calls(self):
        github_team = _make_github_team(members=[])
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", members=["alice"], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=True,
        )

        github_team.add_to_members.assert_not_called()

    def test_model_team_push_to_github_no_change_no_calls(self):
        github_team = _make_github_team(members=["alice"])
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", members=["alice"], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team.add_to_members.assert_not_called()
        github_team.remove_from_members.assert_not_called()

class TestModelTeamPushToGitHubRepositories:
    def test_model_team_push_to_github_adds_new_repo(self, capsys):
        github_team = _make_github_team(members=[])
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", members=[], repositories=[TeamRepository(name="repo1", role="write")])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team._requester.requestJsonAndCheck.assert_called_with(
            "PUT", "https://api.github.test/teams/42/repos/OrgA/repo1", input={"permission": "push"}
        )
        assert "repo1" in capsys.readouterr().out

    def test_model_team_push_to_github_removes_old_repo(self, capsys):
        github_team = _make_github_team(members=[])
        github_team._requester.requestJsonAndCheck.return_value = (None, [{"name": "old-repo", "role_name": "read"}])
        team = Team(name="team1", members=[], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team._requester.requestJsonAndCheck.assert_called_with(
            "DELETE", "https://api.github.test/teams/42/repos/OrgA/old-repo"
        )
        assert "old-repo" in capsys.readouterr().out

    def test_model_team_push_to_github_updates_repo_role(self, capsys):
        github_team = _make_github_team(members=[])
        github_team._requester.requestJsonAndCheck.return_value = (None, [{"name": "repo1", "role_name": "read"}])
        team = Team(name="team1", members=[], repositories=[TeamRepository(name="repo1", role="write")])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team._requester.requestJsonAndCheck.assert_called_with(
            "PUT", "https://api.github.test/teams/42/repos/OrgA/repo1", input={"permission": "push"}
        )
        output = capsys.readouterr().out
        assert "read" in output
        assert "write" in output

    def test_model_team_push_to_github_repo_unchanged_role_skips_update(self):
        github_team = _make_github_team(members=[])
        requestJsonAndCheck = Mock(return_value=(None, [{"name": "repo1", "role_name": "write"}]))
        github_team._requester.requestJsonAndCheck = requestJsonAndCheck
        team = Team(name="team1", members=[], repositories=[TeamRepository(name="repo1", role="write")])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        # Only the GET call, no PUT/DELETE
        requestJsonAndCheck.assert_called_once_with(
            "GET",
            "https://api.github.test/teams/42/repos",
            headers={"Accept": "application/vnd.github.v3.repository+json"},
        )

class TestModelTeamPushToGitHubMetadata:
    def test_model_team_push_to_github_updates_description(self, capsys):
        github_team = _make_github_team(description="old desc")
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", description="new desc", members=[], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team.edit.assert_called_once_with("team1", description="new desc")

    def test_model_team_push_to_github_updates_parent(self):
        parent_github_team = SimpleNamespace(id=99)
        github_team = _make_github_team(description="desc")
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", description="desc", parent="parent-team", members=[], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={"parent-team": parent_github_team},
            dry_run=False,
        )

        github_team.edit.assert_called_once_with("team1", description="desc", parent_team_id=99)

    def test_model_team_push_to_github_metadata_unchanged_skips_edit(self):
        github_team = _make_github_team(description="same desc")
        github_team._requester.requestJsonAndCheck.return_value = (None, [])
        team = Team(name="team1", description="same desc", members=[], repositories=[])

        team.push_to_github(
            client=_make_client(),
            github_org=_make_github_org(),
            github_team=github_team,
            current_github_teams={},
            dry_run=False,
        )

        github_team.edit.assert_not_called()

class TestModelTeamCreateInGitHub:
    def test_model_team_create_in_github_calls_org_create_team(self, capsys):
        created_team = SimpleNamespace(
            id=10,
            url="https://api.github.test/teams/10",
            add_to_members=Mock(),
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        github_org = SimpleNamespace(login="OrgA", create_team=Mock(return_value=created_team))
        team = Team(name="new-team", description="desc", members=[], repositories=[])
        current_github_teams = {}

        team.create_in_github(client=_make_client(), github_org=github_org, current_github_teams=current_github_teams, dry_run=False)

        github_org.create_team.assert_called_once_with(name="new-team", description="desc", privacy="closed")
        assert "new-team" in capsys.readouterr().out

    def test_model_team_create_in_github_adds_members(self):
        created_team = SimpleNamespace(
            id=10,
            url="https://api.github.test/teams/10",
            add_to_members=Mock(),
            _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        github_org = SimpleNamespace(login="OrgA", create_team=Mock(return_value=created_team))
        team = Team(name="new-team", members=["alice", "bob"], repositories=[])

        team.create_in_github(client=_make_client(), github_org=github_org, current_github_teams={}, dry_run=False)

        assert created_team.add_to_members.call_count == 2

    def test_model_team_create_in_github_registers_in_current_teams(self):
        created_team = SimpleNamespace(
            id=10, url="https://api.github.test/teams/10",
            add_to_members=Mock(), _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        github_org = SimpleNamespace(login="OrgA", create_team=Mock(return_value=created_team))
        team = Team(name="new-team", members=[], repositories=[])
        current_github_teams = {}

        team.create_in_github(client=_make_client(), github_org=github_org, current_github_teams=current_github_teams, dry_run=False)

        assert current_github_teams["new-team"] is created_team

    def test_model_team_create_in_github_resolves_parent_team_id(self):
        parent_github_team = SimpleNamespace(id=99)
        created_team = SimpleNamespace(
            id=10, url="https://api.github.test/teams/10",
            add_to_members=Mock(), _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        github_org = SimpleNamespace(login="OrgA", create_team=Mock(return_value=created_team))
        team = Team(name="child-team", parent="parent-team", members=[], repositories=[])

        team.create_in_github(
            client=_make_client(),
            github_org=github_org,
            current_github_teams={"parent-team": parent_github_team},
            dry_run=False,
        )

        github_org.create_team.assert_called_once_with(
            name="child-team", description="", privacy="closed", parent_team_id=99
        )

    def test_model_team_create_in_github_dry_run_skips_api_calls(self, capsys):
        github_org = SimpleNamespace(login="OrgA", create_team=Mock())
        team = Team(name="new-team", members=["alice"], repositories=[])

        team.create_in_github(client=_make_client(), github_org=github_org, current_github_teams={}, dry_run=True)

        github_org.create_team.assert_not_called()
        assert "new-team" in capsys.readouterr().out

    def test_model_team_create_in_github_adds_repo_permissions(self):
        created_team = SimpleNamespace(
            id=10, url="https://api.github.test/teams/10",
            add_to_members=Mock(), _requester=SimpleNamespace(requestJsonAndCheck=Mock()),
        )
        github_org = SimpleNamespace(login="OrgA", create_team=Mock(return_value=created_team))
        team = Team(name="new-team", members=[], repositories=[TeamRepository(name="repo1", role="write")])

        team.create_in_github(client=_make_client(), github_org=github_org, current_github_teams={}, dry_run=False)

        created_team._requester.requestJsonAndCheck.assert_called_once_with(
            "PUT",
            "https://api.github.test/teams/10/repos/OrgA/repo1",
            input={"permission": "push"},
        )

from github_management.model.github.organization import Organization
from github_management.model.github.member import Member
from github_management.model.github.repository import Repository
from github_management.model.github.repository_visibility import RepositoryVisibility
from github_management.model.github.team import Team
from github_management.model.github.role import Role
from github_management.model.diff.change_type import ChangeType

def _make_org(**kwargs):
    defaults = dict(name="OrgX", description="", members=[], teams=[], repositories=[], roles=[])
    defaults.update(kwargs)
    return Organization(**defaults)

def _make_repo(name, description="", topics=None):
    return Repository(
        name=name,
        owner="OrgX",
        description=description,
        archive=False,
        visibility=RepositoryVisibility.PUBLIC,
        topics=topics or [],
        permissions=None,
    )

class TestDiffOrganizationIdentical:
    def test_diff_empty_org_no_changes(self):
        o = _make_org()
        assert o.diff(o, "orgs[OrgX]") == []

    def test_diff_full_org_no_changes(self):
        o = _make_org(
            description="my org",
            members=[Member(login="alice", name="Alice")],
            repositories=[_make_repo("repo1")],
        )
        assert o.diff(o, "path") == []

class TestDiffOrganizationDescriptionChanged:
    def test_diff_description_change_detected(self):
        local = _make_org(description="new")
        remote = _make_org(description="old")
        result = local.diff(remote, "path")
        desc = [c for c in result if "description" in c.path]
        assert len(desc) == 1
        assert desc[0].type == ChangeType.CHANGED

    def test_diff_description_same_no_change(self):
        o = _make_org(description="same")
        assert not any("description" in c.path for c in o.diff(o, "path"))

class TestDiffOrganizationMembersChanged:
    def test_diff_member_added_in_local(self):
        local = _make_org(members=[Member(login="alice", name="Alice")])
        remote = _make_org(members=[])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.ADDED for c in result)

    def test_diff_member_removed(self):
        local = _make_org(members=[])
        remote = _make_org(members=[Member(login="alice", name="Alice")])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.REMOVED for c in result)

    def test_diff_member_name_different_but_same_login_is_changed(self):
        local = _make_org(members=[Member(login="alice", name="Alice New")])
        remote = _make_org(members=[Member(login="alice", name="Alice Old")])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.CHANGED for c in result)

    def test_diff_shared_members_same_no_change(self):
        m = [Member(login="alice", name="Alice"), Member(login="bob", name="Bob")]
        local = _make_org(members=m)
        remote = _make_org(members=m)
        assert not any("members" in c.path for c in local.diff(remote, "path"))

class TestDiffOrganizationRepositoriesChanged:
    def test_diff_repo_added_in_local(self):
        local = _make_org(repositories=[_make_repo("repo1")])
        remote = _make_org(repositories=[])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.ADDED for c in result)

    def test_diff_repo_removed(self):
        local = _make_org(repositories=[])
        remote = _make_org(repositories=[_make_repo("repo1")])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.REMOVED for c in result)

    def test_diff_repo_description_changed(self):
        local = _make_org(repositories=[_make_repo("repo1", description="new")])
        remote = _make_org(repositories=[_make_repo("repo1", description="old")])
        result = local.diff(remote, "path")
        assert any("description" in c.path for c in result)

    def test_diff_two_repos_same_no_change(self):
        repos = [_make_repo("repo1"), _make_repo("repo2")]
        local = _make_org(repositories=repos)
        remote = _make_org(repositories=repos)
        assert not any("repositories" in c.path for c in local.diff(remote, "path"))

class TestDiffOrganizationTeamsChanged:
    def test_diff_team_added_in_local(self):
        local = _make_org(teams=[Team(name="team1", description="t")])
        remote = _make_org(teams=[])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.ADDED for c in result)

    def test_diff_team_removed(self):
        local = _make_org(teams=[])
        remote = _make_org(teams=[Team(name="team1", description="t")])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.REMOVED for c in result)

    def test_diff_none_teams_are_filtered(self):
        local = _make_org(teams=[None, Team(name="team1", description="t")])
        remote = _make_org(teams=[Team(name="team1", description="t")])
        result = local.diff(remote, "path")
        assert result == []

    def test_diff_team_description_changed(self):
        local = _make_org(teams=[Team(name="team1", description="new")])
        remote = _make_org(teams=[Team(name="team1", description="old")])
        result = local.diff(remote, "path")
        assert any("description" in c.path for c in result)

class TestDiffOrganizationRolesChanged:
    def test_diff_role_added_in_local(self):
        local = _make_org(roles=[Role(name="DevRole", description="dev", permissions=[])])
        remote = _make_org(roles=[])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.ADDED for c in result)

    def test_diff_role_removed(self):
        local = _make_org(roles=[])
        remote = _make_org(roles=[Role(name="DevRole", description="dev", permissions=[])])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.REMOVED for c in result)

    def test_diff_role_description_changed(self):
        local = _make_org(roles=[Role(name="DevRole", description="new", permissions=[])])
        remote = _make_org(roles=[Role(name="DevRole", description="old", permissions=[])])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.CHANGED for c in result)

class TestDiffOrganizationMultipleFieldChanges:
    def test_diff_description_and_repo_both_changed(self):
        local = _make_org(
            description="new desc",
            repositories=[_make_repo("repo1", description="new")],
        )
        remote = _make_org(
            description="old desc",
            repositories=[_make_repo("repo1", description="old")],
        )
        result = local.diff(remote, "path")
        assert any("description" in c.path and "repositories" not in c.path for c in result)
        assert any("description" in c.path and "repositories" in c.path for c in result)

from github_management.model.github.team import Team
from github_management.model.github.team_repository import TeamRepository
from github_management.model.diff.change_type import ChangeType


def _make_team(**kwargs):
    defaults = dict(name="team1", description="desc", members=[], parent=None, repositories=[])
    defaults.update(kwargs)
    return Team(**defaults)


class TestDiffTeamIdentical:
    def test_diff_empty_team_no_changes(self):
        t = _make_team()
        assert t.diff(t, "path") == []

    def test_diff_full_team_no_changes(self):
        t = _make_team(
            description="my team",
            members=["alice", "bob"],
            parent="parent_team",
            repositories=[TeamRepository(name="repo1", role="write")],
        )
        assert t.diff(t, "path") == []

class TestDiffTeamDescriptionChanged:
    def test_diff_description_change_type(self):
        local = _make_team(description="new")
        remote = _make_team(description="old")
        result = local.diff(remote, "path")
        desc = [c for c in result if "description" in c.path]
        assert len(desc) == 1
        assert desc[0].type == ChangeType.CHANGED

    def test_diff_description_change_values(self):
        local = _make_team(description="new")
        remote = _make_team(description="old")
        result = local.diff(remote, "path")
        desc = [c for c in result if "description" in c.path][0]
        assert desc.local == "new"
        assert desc.remote == "old"

    def test_diff_description_same_no_change(self):
        t = _make_team(description="same")
        assert not any("description" in c.path for c in t.diff(t, "path"))

class TestDiffTeamParentChanged:
    def test_diff_parent_change_detected(self):
        local = _make_team(parent="new_parent")
        remote = _make_team(parent="old_parent")
        result = local.diff(remote, "path")
        parent = [c for c in result if "parent" in c.path]
        assert len(parent) == 1
        assert parent[0].type == ChangeType.CHANGED

    def test_diff_parent_added(self):
        local = _make_team(parent="parent_team")
        remote = _make_team(parent=None)
        result = local.diff(remote, "path")
        assert any("parent" in c.path for c in result)

    def test_diff_parent_removed(self):
        local = _make_team(parent=None)
        remote = _make_team(parent="parent_team")
        result = local.diff(remote, "path")
        assert any("parent" in c.path for c in result)

    def test_diff_parent_same_none_no_change(self):
        local = _make_team(parent=None)
        remote = _make_team(parent=None)
        assert not any("parent" in c.path for c in local.diff(remote, "path"))

class TestDiffTeamMembersChanged:
    def test_diff_member_added_in_local(self):
        local = _make_team(members=["alice"])
        remote = _make_team(members=[])
        result = local.diff(remote, "path")
        member_changes = [c for c in result if "members" in c.path]
        assert len(member_changes) == 1
        assert member_changes[0].type == ChangeType.ADDED
        assert member_changes[0].local == "alice"

    def test_diff_member_removed(self):
        local = _make_team(members=[])
        remote = _make_team(members=["alice"])
        result = local.diff(remote, "path")
        member_changes = [c for c in result if "members" in c.path]
        assert member_changes[0].type == ChangeType.REMOVED

    def test_diff_shared_members_not_reported(self):
        local = _make_team(members=["shared", "local_only"])
        remote = _make_team(members=["shared", "remote_only"])
        result = local.diff(remote, "path")
        member_vals = [c.local or c.remote for c in result if "members" in c.path]
        assert "shared" not in member_vals

    def test_diff_multiple_members_added(self):
        local = _make_team(members=["a", "b", "c"])
        remote = _make_team(members=[])
        result = local.diff(remote, "path")
        member_changes = [c for c in result if "members" in c.path]
        assert len(member_changes) == 3

class TestDiffTeamRepositoriesChanged:
    def test_diff_repo_added_in_local(self):
        local = _make_team(repositories=[TeamRepository(name="repo1", role="write")])
        remote = _make_team(repositories=[])
        result = local.diff(remote, "teams[team1]")
        assert any(c.type == ChangeType.ADDED for c in result)

    def test_diff_repo_removed(self):
        local = _make_team(repositories=[])
        remote = _make_team(repositories=[TeamRepository(name="repo1", role="read")])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.REMOVED for c in result)

    def test_diff_repo_role_changed(self):
        local = _make_team(repositories=[TeamRepository(name="repo1", role="admin")])
        remote = _make_team(repositories=[TeamRepository(name="repo1", role="read")])
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.CHANGED for c in result)

class TestDiffTeamMultipleFields:
    def test_diff_description_and_members_both_changed(self):
        local = _make_team(description="new", members=["alice"])
        remote = _make_team(description="old", members=[])
        result = local.diff(remote, "path")
        assert any("description" in c.path for c in result)
        assert any("members" in c.path for c in result)

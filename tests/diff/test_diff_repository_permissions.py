import pytest
from github_management.model.github.repository_permissions import RepositoryPermissions
from github_management.model.diff.change_type import ChangeType


def _make_perms(**kwargs):
    defaults = dict(admin=[], maintain=[], write=[], triage=[], read=[])
    defaults.update(kwargs)
    return RepositoryPermissions(**defaults)

class TestDiffRepositoryPermissionsIdentical:
    def test_diff_all_empty_no_changes(self):
        local = _make_perms()
        remote = _make_perms()
        assert local.diff(remote, "path") == []

    def test_diff_same_admin_list_no_changes(self):
        local = _make_perms(admin=["alice", "bob"])
        remote = _make_perms(admin=["alice", "bob"])
        assert local.diff(remote, "path") == []

    def test_diff_same_all_levels_no_changes(self):
        local = _make_perms(admin=["a"], maintain=["b"], write=["c"], triage=["d"], read=["e"])
        remote = _make_perms(admin=["a"], maintain=["b"], write=["c"], triage=["d"], read=["e"])
        assert local.diff(remote, "path") == []

class TestDiffRepositoryPermissionsAdminLevel:
    def test_diff_admin_added_in_local(self):
        local = _make_perms(admin=["alice"])
        remote = _make_perms(admin=[])
        result = local.diff(remote, "repo.permissions")
        assert len(result) == 1
        assert result[0].type == ChangeType.ADDED
        assert result[0].local == "alice"

    def test_diff_admin_removed_from_local(self):
        local = _make_perms(admin=[])
        remote = _make_perms(admin=["alice"])
        result = local.diff(remote, "repo.permissions")
        assert len(result) == 1
        assert result[0].type == ChangeType.REMOVED
        assert result[0].remote == "alice"

    def test_diff_path_contains_admin(self):
        local = _make_perms(admin=["alice"])
        remote = _make_perms(admin=[])
        result = local.diff(remote, "root")
        assert "admin" in result[0].path

class TestDiffRepositoryPermissionsMaintainLevel:
    def test_diff_maintain_added(self):
        local = _make_perms(maintain=["bob"])
        remote = _make_perms(maintain=[])
        result = local.diff(remote, "path")
        assert len(result) == 1
        assert result[0].type == ChangeType.ADDED

    def test_diff_maintain_removed(self):
        local = _make_perms(maintain=[])
        remote = _make_perms(maintain=["bob"])
        result = local.diff(remote, "path")
        assert result[0].type == ChangeType.REMOVED

class TestDiffRepositoryPermissionsWriteLevel:
    def test_diff_write_added(self):
        local = _make_perms(write=["team1"])
        remote = _make_perms(write=[])
        result = local.diff(remote, "path")
        assert result[0].type == ChangeType.ADDED

    def test_diff_write_removed(self):
        local = _make_perms(write=[])
        remote = _make_perms(write=["team1"])
        result = local.diff(remote, "path")
        assert result[0].type == ChangeType.REMOVED

class TestDiffRepositoryPermissionsTriageLevel:
    def test_diff_triage_added(self):
        local = _make_perms(triage=["user1"])
        remote = _make_perms(triage=[])
        result = local.diff(remote, "path")
        assert result[0].type == ChangeType.ADDED

class TestDiffRepositoryPermissionsReadLevel:
    def test_diff_read_added(self):
        local = _make_perms(read=["user2"])
        remote = _make_perms(read=[])
        result = local.diff(remote, "path")
        assert result[0].type == ChangeType.ADDED

class TestDiffRepositoryPermissionsMultipleLevels:
    def test_diff_multiple_levels_changed_independently(self):
        local = _make_perms(admin=["alice_new"], write=["team_new"])
        remote = _make_perms(admin=["alice_old"], write=["team_old"])
        result = local.diff(remote, "path")
        # alice_new added, alice_old removed, team_new added, team_old removed
        assert len(result) == 4

    def test_diff_changes_across_all_levels(self):
        local = _make_perms(admin=["a"], maintain=["b"], write=["c"], triage=["d"], read=["e"])
        remote = _make_perms(admin=["A"], maintain=["B"], write=["C"], triage=["D"], read=["E"])
        result = local.diff(remote, "path")
        # For each level: 1 local added + 1 remote removed = 2 changes per level × 5 levels = 10
        assert len(result) == 10

    def test_diff_some_levels_same_some_different(self):
        local = _make_perms(admin=["alice"], write=["team_new"])
        remote = _make_perms(admin=["alice"], write=["team_old"])
        result = local.diff(remote, "path")
        assert len(result) == 2  # team_new added, team_old removed

class TestDiffRepositoryPermissionsPathPropagation:
    @pytest.mark.parametrize("level", ["admin", "maintain", "write", "triage", "read"])
    def test_diff_path_includes_level_name(self, level):
        local = _make_perms(**{level: ["user1"]})
        remote = _make_perms()
        result = local.diff(remote, "root")
        assert level in result[0].path

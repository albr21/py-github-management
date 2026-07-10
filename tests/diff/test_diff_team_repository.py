import pytest
from github_management.model.github.team_repository import TeamRepository
from github_management.model.diff.change_type import ChangeType


class TestDiffTeamRepositoryIdentical:
    def test_diff_same_role_no_changes(self):
        local = TeamRepository(name="repo1", role="write")
        remote = TeamRepository(name="repo1", role="write")
        assert local.diff(remote, "path[repo1]") == []

    def test_diff_admin_role_no_changes(self):
        local = TeamRepository(name="repo1", role="admin")
        remote = TeamRepository(name="repo1", role="admin")
        assert local.diff(remote, "path[repo1]") == []

class TestDiffTeamRepositoryRoleChanged:
    def test_diff_role_change_produces_one_change(self):
        local = TeamRepository(name="repo1", role="admin")
        remote = TeamRepository(name="repo1", role="read")
        result = local.diff(remote, "path[repo1]")
        assert len(result) == 1

    def test_diff_role_change_type_is_changed(self):
        local = TeamRepository(name="repo1", role="admin")
        remote = TeamRepository(name="repo1", role="read")
        result = local.diff(remote, "path[repo1]")
        assert result[0].type == ChangeType.CHANGED

    def test_diff_role_change_local_value(self):
        local = TeamRepository(name="repo1", role="admin")
        remote = TeamRepository(name="repo1", role="read")
        result = local.diff(remote, "path[repo1]")
        assert result[0].local == "admin"

    def test_diff_role_change_remote_value(self):
        local = TeamRepository(name="repo1", role="admin")
        remote = TeamRepository(name="repo1", role="read")
        result = local.diff(remote, "path[repo1]")
        assert result[0].remote == "read"

    def test_diff_role_change_path_contains_role(self):
        local = TeamRepository(name="repo1", role="admin")
        remote = TeamRepository(name="repo1", role="read")
        result = local.diff(remote, "teams[t1]")
        assert "role" in result[0].path

@pytest.mark.parametrize("local_role,remote_role", [
    ("read", "write"),
    ("write", "admin"),
    ("admin", "maintain"),
    ("maintain", "triage"),
    ("triage", "read"),
])
def test_diff_team_repository_role_change_parametrized(local_role, remote_role):
    local = TeamRepository(name="repo1", role=local_role)
    remote = TeamRepository(name="repo1", role=remote_role)
    result = local.diff(remote, "path")
    assert len(result) == 1
    assert result[0].type == ChangeType.CHANGED
    assert result[0].local == local_role
    assert result[0].remote == remote_role

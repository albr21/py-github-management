from github_management.model.github.role import Role
from github_management.model.github.base_role import BaseRole
from github_management.model.diff.change_type import ChangeType


class TestDiffRoleIdentical:
    def test_diff_same_role_no_changes(self):
        local = Role(name="Dev", description="desc", permissions=["add_label"], base_role=BaseRole.READ)
        remote = Role(name="Dev", description="desc", permissions=["add_label"], base_role=BaseRole.READ)
        assert local.diff(remote, "roles[Dev]") == []

    def test_diff_same_role_no_base_no_changes(self):
        local = Role(name="Dev", description="desc", permissions=[], base_role=None)
        remote = Role(name="Dev", description="desc", permissions=[], base_role=None)
        assert local.diff(remote, "path") == []

class TestDiffRoleDescriptionChanged:
    def test_diff_description_change_produces_change(self):
        local = Role(name="r", description="new desc", permissions=[], base_role=None)
        remote = Role(name="r", description="old desc", permissions=[], base_role=None)
        result = local.diff(remote, "path")
        assert len(result) == 1
        assert result[0].type == ChangeType.CHANGED

    def test_diff_description_change_local_value(self):
        local = Role(name="r", description="new", permissions=[], base_role=None)
        remote = Role(name="r", description="old", permissions=[], base_role=None)
        result = local.diff(remote, "path")
        assert result[0].local == "new"
        assert result[0].remote == "old"

    def test_diff_description_change_to_empty(self):
        local = Role(name="r", description="", permissions=[], base_role=None)
        remote = Role(name="r", description="some desc", permissions=[], base_role=None)
        result = local.diff(remote, "path")
        assert result[0].type == ChangeType.CHANGED

class TestDiffRoleBaseRoleChanged:
    def test_diff_base_role_change_produces_change(self):
        local = Role(name="r", description="", permissions=[], base_role=BaseRole.WRITE)
        remote = Role(name="r", description="", permissions=[], base_role=BaseRole.READ)
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.CHANGED for c in result)

    def test_diff_base_role_added_local_only(self):
        local = Role(name="r", description="", permissions=[], base_role=BaseRole.WRITE)
        remote = Role(name="r", description="", permissions=[], base_role=None)
        result = local.diff(remote, "path")
        assert any(c.local == "write" for c in result)

    def test_diff_base_role_removed_remote_only(self):
        local = Role(name="r", description="", permissions=[], base_role=None)
        remote = Role(name="r", description="", permissions=[], base_role=BaseRole.READ)
        result = local.diff(remote, "path")
        assert any(c.remote == "read" for c in result)

class TestDiffRolePermissionsChanged:
    def test_diff_permission_added_in_local(self):
        local = Role(name="r", description="", permissions=["add_label"], base_role=None)
        remote = Role(name="r", description="", permissions=[], base_role=None)
        result = local.diff(remote, "path")
        assert len(result) == 1
        assert result[0].type == ChangeType.ADDED
        assert result[0].local == "add_label"

    def test_diff_permission_removed_from_local(self):
        local = Role(name="r", description="", permissions=[], base_role=None)
        remote = Role(name="r", description="", permissions=["delete_issue"], base_role=None)
        result = local.diff(remote, "path")
        assert len(result) == 1
        assert result[0].type == ChangeType.REMOVED
        assert result[0].remote == "delete_issue"

    def test_diff_shared_permissions_not_reported(self):
        local = Role(name="r", description="", permissions=["shared", "local_perm"], base_role=None)
        remote = Role(name="r", description="", permissions=["shared", "remote_perm"], base_role=None)
        result = local.diff(remote, "path")
        values = [c.local or c.remote for c in result]
        assert "shared" not in values

class TestDiffRoleMultipleFields:
    def test_diff_description_and_permissions_both_changed(self):
        local = Role(name="r", description="new", permissions=["add_label"], base_role=None)
        remote = Role(name="r", description="old", permissions=[], base_role=None)
        result = local.diff(remote, "path")
        # 1 description change + 1 permission added = 2
        assert len(result) == 2

    def test_diff_all_fields_different(self):
        local = Role(name="r", description="A", permissions=["p1"], base_role=BaseRole.WRITE)
        remote = Role(name="r", description="B", permissions=["p2"], base_role=BaseRole.READ)
        result = local.diff(remote, "path")
        # 1 description + 1 base_role + 1 p1 added + 1 p2 removed = 4
        assert len(result) == 4

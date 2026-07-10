import pytest
from github_management.model.diff.utils import diff_list_by_name, diff_list_by_login
from github_management.model.diff.change_type import ChangeType
from github_management.model.github.team_repository import TeamRepository
from github_management.model.github.member import Member

class TestDiffListByNameBothEmpty:
    def test_diff_no_changes(self):
        assert diff_list_by_name([], [], "path") == []

class TestDiffListByNameIdentical:
    def test_diff_same_single_item_no_changes(self):
        local = [TeamRepository(name="repo1", role="write")]
        remote = [TeamRepository(name="repo1", role="write")]
        result = diff_list_by_name(local, remote, "path")
        assert result == []

    def test_diff_same_multiple_items_no_changes(self):
        local = [TeamRepository(name="r1", role="read"), TeamRepository(name="r2", role="write")]
        remote = [TeamRepository(name="r1", role="read"), TeamRepository(name="r2", role="write")]
        assert diff_list_by_name(local, remote, "path") == []

class TestDiffListByNameLocalOnly:
    def test_diff_item_only_in_local_is_added(self):
        local = [TeamRepository(name="repo1", role="write")]
        result = diff_list_by_name(local, [], "teams")
        assert len(result) == 1
        assert result[0].type == ChangeType.ADDED
        assert result[0].path == "teams[repo1]"
        assert result[0].local.name == "repo1"
        assert result[0].remote is None

    def test_diff_multiple_local_only_all_added(self):
        local = [TeamRepository(name="a", role="read"), TeamRepository(name="b", role="write")]
        result = diff_list_by_name(local, [], "path")
        assert len(result) == 2
        assert all(c.type == ChangeType.ADDED for c in result)

class TestDiffListByNameRemoteOnly:
    def test_diff_item_only_in_remote_is_removed(self):
        remote = [TeamRepository(name="repo1", role="write")]
        result = diff_list_by_name([], remote, "teams")
        assert len(result) == 1
        assert result[0].type == ChangeType.REMOVED
        assert result[0].path == "teams[repo1]"
        assert result[0].remote.name == "repo1"
        assert result[0].local is None

    def test_diff_multiple_remote_only_all_removed(self):
        remote = [TeamRepository(name="a", role="read"), TeamRepository(name="b", role="write")]
        result = diff_list_by_name([], remote, "path")
        assert len(result) == 2
        assert all(c.type == ChangeType.REMOVED for c in result)

class TestDiffListByNameChanged:
    def test_diff_same_name_different_role_is_changed(self):
        local = [TeamRepository(name="repo1", role="admin")]
        remote = [TeamRepository(name="repo1", role="read")]
        result = diff_list_by_name(local, remote, "path")
        assert len(result) == 1
        assert result[0].type == ChangeType.CHANGED

    def test_diff_same_name_same_role_no_change(self):
        local = [TeamRepository(name="repo1", role="write")]
        remote = [TeamRepository(name="repo1", role="write")]
        result = diff_list_by_name(local, remote, "path")
        assert result == []

class TestDiffListByNameSortedByName:
    def test_diff_results_from_added_items_sorted(self):
        local = [TeamRepository(name="z_repo", role="read"), TeamRepository(name="a_repo", role="read")]
        result = diff_list_by_name(local, [], "path")
        paths = [c.path for c in result]
        assert paths == sorted(paths)

class TestDiffListByNameMixed:
    def test_diff_mixed_added_removed_and_changed(self):
        local = [
            TeamRepository(name="shared", role="write"),  # changed role
            TeamRepository(name="only_local", role="read"),  # added
        ]
        remote = [
            TeamRepository(name="shared", role="read"),
            TeamRepository(name="only_remote", role="admin"),  # removed
        ]
        result = diff_list_by_name(local, remote, "path")
        types = {c.type for c in result}
        assert ChangeType.ADDED in types
        assert ChangeType.REMOVED in types
        assert ChangeType.CHANGED in types

    def test_diff_path_contains_name(self):
        local = [TeamRepository(name="my_repo", role="write")]
        result = diff_list_by_name(local, [], "teams")
        assert "my_repo" in result[0].path

class TestDiffListByNameNoneFiltered:
    def test_diff_none_items_in_local_ignored(self):
        local = [None, TeamRepository(name="repo1", role="write")]
        remote = [TeamRepository(name="repo1", role="write")]
        # Should not raise and should produce no diff since repo1 is same
        result = diff_list_by_name(local, remote, "path")
        assert result == []

    def test_diff_none_items_in_remote_ignored(self):
        local = [TeamRepository(name="repo1", role="write")]
        remote = [None, TeamRepository(name="repo1", role="write")]
        result = diff_list_by_name(local, remote, "path")
        assert result == []
class TestDiffListByLoginBothEmpty:
    def test_diff_no_changes(self):
        assert diff_list_by_login([], [], "path") == []

class TestDiffListByLoginLocalOnly:
    def test_diff_member_only_local_is_added(self):
        local = [Member(login="user1", name="User One")]
        result = diff_list_by_login(local, [], "members")
        assert len(result) == 1
        assert result[0].type == ChangeType.ADDED
        assert result[0].path == "members[user1]"

    def test_diff_member_only_remote_is_removed(self):
        remote = [Member(login="user2", name="User Two")]
        result = diff_list_by_login([], remote, "members")
        assert len(result) == 1
        assert result[0].type == ChangeType.REMOVED

    def test_diff_same_member_no_change(self):
        m = [Member(login="user1", name="User One")]
        assert diff_list_by_login(m, m, "path") == []

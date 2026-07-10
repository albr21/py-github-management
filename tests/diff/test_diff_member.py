from github_management.model.github.member import Member
from github_management.model.diff.change_type import ChangeType

class TestDiffMemberIdentical:
    def test_diff_same_member_no_changes(self):
        local = Member(login="user1", name="Alice")
        remote = Member(login="user1", name="Alice")
        assert local.diff(remote, "members[user1]") == []

class TestDiffMemberNameChanged:
    def test_diff_name_change_produces_one_change(self):
        local = Member(login="user1", name="Alice New")
        remote = Member(login="user1", name="Alice Old")
        result = local.diff(remote, "members[user1]")
        assert len(result) == 1

    def test_diff_name_change_type_is_changed(self):
        local = Member(login="user1", name="Alice New")
        remote = Member(login="user1", name="Alice Old")
        result = local.diff(remote, "members[user1]")
        assert result[0].type == ChangeType.CHANGED

    def test_diff_name_change_local_value(self):
        local = Member(login="user1", name="Alice New")
        remote = Member(login="user1", name="Alice Old")
        result = local.diff(remote, "members[user1]")
        assert result[0].local == "Alice New"

    def test_diff_name_change_remote_value(self):
        local = Member(login="user1", name="Alice New")
        remote = Member(login="user1", name="Alice Old")
        result = local.diff(remote, "members[user1]")
        assert result[0].remote == "Alice Old"

    def test_diff_name_change_path_contains_name(self):
        local = Member(login="user1", name="Alice New")
        remote = Member(login="user1", name="Alice Old")
        result = local.diff(remote, "members[user1]")
        assert "name" in result[0].path

class TestDiffMemberEmptyNameToValue:
    def test_diff_change_from_empty_to_value(self):
        local = Member(login="user1", name="Alice")
        remote = Member(login="user1", name="")
        result = local.diff(remote, "path")
        assert len(result) == 1
        assert result[0].local == "Alice"
        assert result[0].remote == ""

class TestDiffMemberPathPropagation:
    def test_diff_custom_path_used_in_change(self):
        local = Member(login="u", name="New")
        remote = Member(login="u", name="Old")
        result = local.diff(remote, "orgs[X].members[u]")
        assert result[0].path.startswith("orgs[X].members[u]")

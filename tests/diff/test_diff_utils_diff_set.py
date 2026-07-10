from github_management.model.diff.utils import diff_set
from github_management.model.diff.change_type import ChangeType

class TestDiffSetBothEmpty:
    def test_diff_no_changes(self):
        result = diff_set([], [], "path")
        assert result == []

class TestDiffSetIdentical:
    def test_diff_same_single_item_no_changes(self):
        result = diff_set(["topic1"], ["topic1"], "path")
        assert result == []

    def test_diff_same_multiple_items_no_changes(self):
        result = diff_set(["a", "b", "c"], ["a", "b", "c"], "path")
        assert result == []

    def test_diff_order_does_not_matter(self):
        result = diff_set(["c", "a", "b"], ["b", "c", "a"], "path")
        assert result == []

class TestDiffSetOnlyLocalItems:
    def test_diff_single_item_local_only_is_added(self):
        result = diff_set(["new_topic"], [], "repos.topics")
        assert len(result) == 1
        assert result[0].type == ChangeType.ADDED
        assert result[0].local == "new_topic"
        assert result[0].remote is None
        assert result[0].path == "repos.topics"

    def test_diff_multiple_local_items_all_added(self):
        result = diff_set(["a", "b", "c"], [], "path")
        assert len(result) == 3
        assert all(c.type == ChangeType.ADDED for c in result)

    def test_diff_local_only_sorted(self):
        result = diff_set(["z", "a", "m"], [], "path")
        local_values = [c.local for c in result]
        assert local_values == sorted(local_values)

class TestDiffSetOnlyRemoteItems:
    def test_diff_single_item_remote_only_is_removed(self):
        result = diff_set([], ["old_topic"], "repos.topics")
        assert len(result) == 1
        assert result[0].type == ChangeType.REMOVED
        assert result[0].remote == "old_topic"
        assert result[0].local is None

    def test_diff_multiple_remote_items_all_removed(self):
        result = diff_set([], ["x", "y", "z"], "path")
        assert len(result) == 3
        assert all(c.type == ChangeType.REMOVED for c in result)

    def test_diff_remote_only_sorted(self):
        result = diff_set([], ["z", "a", "m"], "path")
        remote_values = [c.remote for c in result]
        assert remote_values == sorted(remote_values)

class TestDiffSetMixed:
    def test_diff_shared_not_included(self):
        result = diff_set(["shared", "local_new"], ["shared", "remote_old"], "path")
        paths = [c.local or c.remote for c in result]
        assert "shared" not in paths

    def test_diff_added_and_removed_present(self):
        result = diff_set(["shared", "local_new"], ["shared", "remote_old"], "path")
        types = {c.type for c in result}
        assert ChangeType.ADDED in types
        assert ChangeType.REMOVED in types

    def test_diff_exact_counts(self):
        result = diff_set(["a", "b", "common"], ["c", "d", "common"], "path")
        added = [c for c in result if c.type == ChangeType.ADDED]
        removed = [c for c in result if c.type == ChangeType.REMOVED]
        assert len(added) == 2
        assert len(removed) == 2

class TestDiffSetDuplicatesInInput:
    def test_diff_duplicates_in_local_treated_as_set(self):
        result = diff_set(["a", "a", "a"], ["a"], "path")
        assert result == []

    def test_diff_duplicates_in_remote_treated_as_set(self):
        result = diff_set(["a"], ["a", "a", "a"], "path")
        assert result == []

class TestDiffSetPathPropagation:
    def test_diff_path_is_used_in_changes(self):
        result = diff_set(["x"], [], "my.custom.path")
        assert result[0].path == "my.custom.path"

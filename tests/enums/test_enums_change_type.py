import pytest
from github_management.model.diff.change_type import ChangeType


class TestEnumsChangeTypeValues:
    def test_enums_added_value(self):
        assert ChangeType.ADDED.value == "added"

    def test_enums_removed_value(self):
        assert ChangeType.REMOVED.value == "removed"

    def test_enums_changed_value(self):
        assert ChangeType.CHANGED.value == "changed"

class TestEnumsChangeTypeFromValue:
    def test_enums_from_string_added(self):
        assert ChangeType("added") == ChangeType.ADDED

    def test_enums_from_string_removed(self):
        assert ChangeType("removed") == ChangeType.REMOVED

    def test_enums_from_string_changed(self):
        assert ChangeType("changed") == ChangeType.CHANGED

    def test_enums_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ChangeType("unknown")

class TestEnumsChangeTypeMembers:
    def test_enums_all_members_present(self):
        members = {e.name for e in ChangeType}
        assert members == {"ADDED", "REMOVED", "CHANGED"}

    def test_enums_count(self):
        assert len(ChangeType) == 3

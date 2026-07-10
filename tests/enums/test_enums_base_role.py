import pytest
from github_management.model.github.base_role import BaseRole


class TestEnumsBaseRoleValues:
    def test_enums_read_value(self):
        assert BaseRole.READ.value == "read"

    def test_enums_triage_value(self):
        assert BaseRole.TRIAGE.value == "triage"

    def test_enums_write_value(self):
        assert BaseRole.WRITE.value == "write"

    def test_enums_maintain_value(self):
        assert BaseRole.MAINTAIN.value == "maintain"

class TestEnumsBaseRoleFromValue:
    def test_enums_from_string_read(self):
        assert BaseRole("read") == BaseRole.READ

    def test_enums_from_string_maintain(self):
        assert BaseRole("maintain") == BaseRole.MAINTAIN

    def test_enums_invalid_value_raises(self):
        with pytest.raises(ValueError):
            BaseRole("admin")

class TestEnumsBaseRoleMembers:
    def test_enums_all_members_present(self):
        members = {e.name for e in BaseRole}
        assert members == {"READ", "TRIAGE", "WRITE", "MAINTAIN"}

    def test_enums_count(self):
        assert len(BaseRole) == 4

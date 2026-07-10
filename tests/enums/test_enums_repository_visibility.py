import pytest
from github_management.model.github.repository_visibility import RepositoryVisibility


class TestEnumsRepositoryVisibilityValues:
    def test_enums_public_value(self):
        assert RepositoryVisibility.PUBLIC.value == "public"

    def test_enums_private_value(self):
        assert RepositoryVisibility.PRIVATE.value == "private"

    def test_enums_internal_value(self):
        assert RepositoryVisibility.INTERNAL.value == "internal"

    def test_enums_unknown_value(self):
        assert RepositoryVisibility.UNKNOWN.value == "unknown"

class TestEnumsRepositoryVisibilityFromValue:
    def test_enums_from_string_public(self):
        assert RepositoryVisibility("public") == RepositoryVisibility.PUBLIC

    def test_enums_from_string_private(self):
        assert RepositoryVisibility("private") == RepositoryVisibility.PRIVATE

    def test_enums_from_string_internal(self):
        assert RepositoryVisibility("internal") == RepositoryVisibility.INTERNAL

    def test_enums_from_string_unknown(self):
        assert RepositoryVisibility("unknown") == RepositoryVisibility.UNKNOWN

    def test_enums_invalid_value_raises(self):
        with pytest.raises(ValueError):
            RepositoryVisibility("other")

class TestEnumsRepositoryVisibilityMembers:
    def test_enums_count(self):
        assert len(RepositoryVisibility) == 4

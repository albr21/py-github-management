from github_management.model.github.role import Role
from github_management.model.github.base_role import BaseRole

class TestSerializationRoleFromDict:
    def test_serialization_role_basic_fields(self):
        r = Role.from_dict({"name": "Dev", "description": "dev role", "permissions": ["add_label"], "base_role": "write"})
        assert r.name == "Dev"
        assert r.description == "dev role"
        assert r.permissions == ["add_label"]
        assert r.base_role == BaseRole.WRITE

    def test_serialization_role_base_role_none(self):
        r = Role.from_dict({"name": "Dev", "permissions": [], "base_role": None})
        assert r.base_role is None

    def test_serialization_role_permissions_default_empty(self):
        r = Role.from_dict({"name": "Dev"})
        assert r.permissions == []

    def test_serialization_role_description_default_empty(self):
        r = Role.from_dict({"name": "Dev"})
        assert r.description == ""

class TestSerializationRoleToDict:
    def test_serialization_role_all_keys_present(self):
        r = Role(name="Dev", description="d", permissions=["p1"], base_role=BaseRole.READ)
        d = r.to_dict()
        assert set(d.keys()) == {"name", "description", "permissions", "base_role"}

    def test_serialization_role_base_role_stored_as_string(self):
        r = Role(name="Dev", description="", permissions=[], base_role=BaseRole.WRITE)
        assert r.to_dict()["base_role"] == "write"

    def test_serialization_role_base_role_none_stored_as_none(self):
        r = Role(name="Dev", description="", permissions=[], base_role=None)
        assert r.to_dict()["base_role"] is None

class TestSerializationRoleRoundtrip:
    def test_serialization_role_roundtrip_with_base_role(self):
        d = {"name": "Dev", "description": "desc", "permissions": ["add_label"], "base_role": "read"}
        assert Role.from_dict(d).to_dict() == d

    def test_serialization_role_roundtrip_no_base_role(self):
        d = {"name": "Dev", "description": "", "permissions": [], "base_role": None}
        assert Role.from_dict(d).to_dict() == d

from github_management.model.github.member import Member

class TestSerializationMemberFromDict:
    def test_serialization_member_basic_fields(self):
        m = Member.from_dict({"login": "alice", "name": "Alice Smith"})
        assert m.login == "alice"
        assert m.name == "Alice Smith"

    def test_serialization_member_empty_name(self):
        m = Member.from_dict({"login": "alice", "name": ""})
        assert m.name == ""

class TestSerializationMemberToDict:
    def test_serialization_member_contains_login_and_name(self):
        m = Member(login="bob", name="Bob Jones")
        d = m.to_dict()
        assert d["login"] == "bob"
        assert d["name"] == "Bob Jones"

    def test_serialization_member_keys_only_login_and_name(self):
        m = Member(login="bob", name="Bob")
        assert set(m.to_dict().keys()) == {"login", "name"}

class TestSerializationMemberRoundtrip:
    def test_serialization_member_roundtrip_preserves_all_fields(self):
        original = {"login": "user1", "name": "User One"}
        assert Member.from_dict(original).to_dict() == original

    def test_serialization_member_roundtrip_from_instance(self):
        m = Member(login="x", name="X User")
        assert Member.from_dict(m.to_dict()).login == "x"
        assert Member.from_dict(m.to_dict()).name == "X User"

class TestSerializationMemberStr:
    def test_serialization_member_str_contains_class_name(self):
        m = Member(login="alice", name="Alice")
        assert "Member" in str(m)

    def test_serialization_member_str_contains_login(self):
        m = Member(login="alice", name="Alice")
        assert "alice" in str(m)

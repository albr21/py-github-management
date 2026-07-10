from github_management.model.github.team import Team
from github_management.model.github.team_repository import TeamRepository

class TestSerializationTeamFromDict:
    def test_serialization_team_basic_fields(self):
        d = {
            "name": "team1",
            "description": "desc",
            "members": ["alice", "bob"],
            "parent": "parent_team",
            "repositories": [{"name": "repo1", "role": "write"}],
        }
        t = Team.from_dict(d)
        assert t.name == "team1"
        assert t.description == "desc"
        assert t.members == ["alice", "bob"]
        assert t.parent == "parent_team"
        assert len(t.repositories) == 1
        assert t.repositories[0].name == "repo1"
        assert t.repositories[0].role == "write"

    def test_serialization_team_parent_none(self):
        t = Team.from_dict({"name": "t", "parent": None})
        assert t.parent is None

    def test_serialization_team_members_default_empty(self):
        t = Team.from_dict({"name": "t"})
        assert t.members == []

    def test_serialization_team_repositories_default_empty(self):
        t = Team.from_dict({"name": "t"})
        assert t.repositories == []

    def test_serialization_team_description_default_empty(self):
        t = Team.from_dict({"name": "t"})
        assert t.description == ""

class TestSerializationTeamToDict:
    def test_serialization_team_all_keys_present(self):
        t = Team(name="t", description="d", members=[], parent=None, repositories=[])
        assert set(t.to_dict().keys()) == {"name", "description", "members", "parent", "repositories"}

    def test_serialization_team_repositories_serialized(self):
        t = Team(name="t", description="", members=[], parent=None,
                 repositories=[TeamRepository(name="r1", role="read")])
        d = t.to_dict()
        assert d["repositories"] == [{"name": "r1", "role": "read"}]

class TestSerializationTeamRoundtrip:
    def test_serialization_team_roundtrip_full(self):
        d = {
            "name": "team1",
            "description": "dev team",
            "members": ["alice", "bob"],
            "parent": None,
            "repositories": [{"name": "repo1", "role": "write"}],
        }
        assert Team.from_dict(d).to_dict() == d

    def test_serialization_team_roundtrip_empty(self):
        d = {"name": "t", "description": "", "members": [], "parent": None, "repositories": []}
        assert Team.from_dict(d).to_dict() == d

    def test_serialization_team_roundtrip_with_parent(self):
        d = {"name": "child", "description": "c", "members": [], "parent": "parent_team", "repositories": []}
        assert Team.from_dict(d).to_dict() == d

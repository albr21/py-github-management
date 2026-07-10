from github_management.model.github.team_repository import TeamRepository

class TestSerializationTeamRepositoryFromDict:
    def test_serialization_team_repository_basic_fields(self):
        tr = TeamRepository.from_dict({"name": "repo1", "role": "write"})
        assert tr.name == "repo1"
        assert tr.role == "write"


class TestSerializationTeamRepositoryToDict:
    def test_serialization_team_repository_contains_name_and_role(self):
        tr = TeamRepository(name="repo1", role="admin")
        d = tr.to_dict()
        assert d["name"] == "repo1"
        assert d["role"] == "admin"

    def test_serialization_team_repository_keys(self):
        tr = TeamRepository(name="r", role="read")
        assert set(tr.to_dict().keys()) == {"name", "role"}


class TestSerializationTeamRepositoryRoundtrip:
    def test_serialization_team_repository_roundtrip(self):
        original = {"name": "my_repo", "role": "maintain"}
        assert TeamRepository.from_dict(original).to_dict() == original

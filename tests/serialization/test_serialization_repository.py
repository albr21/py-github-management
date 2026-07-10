from github_management.model.github.repository import Repository
from github_management.model.github.repository_visibility import RepositoryVisibility
from github_management.model.github.repository_permissions import RepositoryPermissions

def _base_dict(**overrides):
    d = {
        "name": "repo1",
        "owner": "org1",
        "description": "desc",
        "archive": False,
        "visibility": "public",
        "topics": [],
        "permissions": None,
    }
    d.update(overrides)
    return d

class TestSerializationRepositoryFromDict:
    def test_serialization_repository_basic_fields(self):
        r = Repository.from_dict(_base_dict())
        assert r.name == "repo1"
        assert r.owner == "org1"
        assert r.description == "desc"
        assert r.archive is False
        assert r.visibility == RepositoryVisibility.PUBLIC
        assert r.topics == []
        assert r.permissions is None

    def test_serialization_repository_visibility_private(self):
        r = Repository.from_dict(_base_dict(visibility="private"))
        assert r.visibility == RepositoryVisibility.PRIVATE

    def test_serialization_repository_visibility_internal(self):
        r = Repository.from_dict(_base_dict(visibility="internal"))
        assert r.visibility == RepositoryVisibility.INTERNAL

    def test_serialization_repository_archive_true(self):
        r = Repository.from_dict(_base_dict(archive=True))
        assert r.archive is True

    def test_serialization_repository_topics_loaded(self):
        r = Repository.from_dict(_base_dict(topics=["python", "ml"]))
        assert r.topics == ["python", "ml"]

    def test_serialization_repository_permissions_loaded(self):
        perm_data = {"admin": ["alice"], "maintain": [], "write": [], "triage": [], "read": []}
        r = Repository.from_dict(_base_dict(permissions=perm_data))
        assert r.permissions is not None
        assert r.permissions.admin == ["alice"]

    def test_serialization_repository_description_defaults_empty_string(self):
        d = _base_dict()
        del d["description"]
        r = Repository.from_dict(d)
        assert r.description == ""

    def test_serialization_repository_archive_defaults_false(self):
        d = _base_dict()
        del d["archive"]
        r = Repository.from_dict(d)
        assert r.archive is False

class TestSerializationRepositoryToDict:
    def test_serialization_repository_all_keys_present(self):
        r = Repository(name="r", owner="o", description="d", archive=False,
                       visibility=RepositoryVisibility.PUBLIC, topics=[], permissions=None)
        d = r.to_dict()
        assert set(d.keys()) == {"name", "owner", "description", "archive", "visibility", "topics", "permissions"}

    def test_serialization_repository_visibility_stored_as_string(self):
        r = Repository(name="r", owner="o", visibility=RepositoryVisibility.PRIVATE,
                       description="", archive=False, topics=[], permissions=None)
        assert r.to_dict()["visibility"] == "private"

    def test_serialization_repository_permissions_none_stored_as_none(self):
        r = Repository(name="r", owner="o", description="", archive=False,
                       visibility=RepositoryVisibility.PUBLIC, topics=[], permissions=None)
        assert r.to_dict()["permissions"] is None

    def test_serialization_repository_permissions_stored_as_dict(self):
        perms = RepositoryPermissions(admin=["alice"], maintain=[], write=[], triage=[], read=[])
        r = Repository(name="r", owner="o", description="", archive=False,
                       visibility=RepositoryVisibility.PUBLIC, topics=[], permissions=perms)
        d = r.to_dict()
        assert d["permissions"]["admin"] == ["alice"]

class TestSerializationRepositoryRoundtrip:
    def test_serialization_repository_roundtrip_basic(self):
        d = _base_dict()
        r = Repository.from_dict(d)
        assert r.to_dict() == d

    def test_serialization_repository_roundtrip_with_topics(self):
        d = _base_dict(topics=["python", "ml"])
        assert Repository.from_dict(d).to_dict() == d

    def test_serialization_repository_roundtrip_archived_internal(self):
        d = _base_dict(archive=True, visibility="internal")
        assert Repository.from_dict(d).to_dict() == d

    def test_serialization_repository_roundtrip_with_permissions(self):
        perm = {"admin": ["alice"], "maintain": ["bob"], "write": [], "triage": [], "read": []}
        d = _base_dict(permissions=perm)
        assert Repository.from_dict(d).to_dict() == d

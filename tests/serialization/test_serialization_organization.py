from github_management.model.github.organization import Organization
from github_management.model.github.member import Member
from github_management.model.github.team import Team
from github_management.model.github.role import Role
from github_management.model.github.repository import Repository
from github_management.model.github.repository_visibility import RepositoryVisibility

def _minimal_org_dict(**overrides):
    d = {
        "name": "OrgX",
        "description": "",
        "members": [],
        "teams": [],
        "roles": [],
        "repositories": [],
    }
    d.update(overrides)
    return d

class TestSerializationOrganizationFromDict:
    def test_serialization_organization_name_and_description(self):
        o = Organization.from_dict(_minimal_org_dict(name="Acme", description="Acme Corp"))
        assert o.name == "Acme"
        assert o.description == "Acme Corp"

    def test_serialization_organization_members_loaded(self):
        d = _minimal_org_dict(members=[{"login": "alice", "name": "Alice"}])
        o = Organization.from_dict(d)
        assert len(o.members) == 1
        assert o.members[0].login == "alice"

    def test_serialization_organization_teams_loaded(self):
        d = _minimal_org_dict(teams=[{"name": "t1", "description": "", "members": [], "parent": None, "repositories": []}])
        o = Organization.from_dict(d)
        assert len(o.teams) == 1
        assert o.teams[0].name == "t1"

    def test_serialization_organization_roles_loaded(self):
        d = _minimal_org_dict(roles=[{"name": "DevRole", "description": "", "permissions": [], "base_role": None}])
        o = Organization.from_dict(d)
        assert len(o.roles) == 1
        assert o.roles[0].name == "DevRole"

    def test_serialization_organization_repositories_loaded(self):
        repo = {
            "name": "repo1", "owner": "OrgX", "description": "", "archive": False,
            "visibility": "public", "topics": [], "permissions": None,
        }
        d = _minimal_org_dict(repositories=[repo])
        o = Organization.from_dict(d)
        assert len(o.repositories) == 1
        assert o.repositories[0].name == "repo1"

    def test_serialization_organization_none_team_in_list(self):
        d = _minimal_org_dict(teams=[None])
        o = Organization.from_dict(d)
        assert o.teams[0] is None

class TestSerializationOrganizationToDict:
    def test_serialization_organization_all_keys_present(self):
        o = Organization(name="O", description="", members=[], teams=[], repositories=[], roles=[])
        assert set(o.to_dict().keys()) == {"name", "description", "members", "teams", "roles", "repositories"}

class TestSerializationOrganizationRoundtrip:
    def test_serialization_organization_roundtrip_empty(self):
        d = _minimal_org_dict()
        assert Organization.from_dict(d).to_dict() == d

    def test_serialization_organization_roundtrip_with_members(self):
        d = _minimal_org_dict(members=[{"login": "alice", "name": "Alice"}])
        assert Organization.from_dict(d).to_dict() == d

    def test_serialization_organization_roundtrip_with_team(self):
        d = _minimal_org_dict(teams=[
            {"name": "t1", "description": "desc", "members": ["alice"], "parent": None, "repositories": []}
        ])
        assert Organization.from_dict(d).to_dict() == d

    def test_serialization_organization_roundtrip_with_role(self):
        d = _minimal_org_dict(roles=[
            {"name": "DevRole", "description": "d", "permissions": ["add_label"], "base_role": "write"}
        ])
        assert Organization.from_dict(d).to_dict() == d

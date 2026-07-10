import yaml
from github_management.model.github.github_management import GitHubManagement
from github_management.model.github.user import User
from github_management.model.github.organization import Organization

def _user_dict(name="testuser"):
    return {"name": name, "repositories": []}

def _org_dict(name="OrgA"):
    return {
        "name": name,
        "description": "",
        "members": [],
        "teams": [],
        "roles": [],
        "repositories": [],
    }

class TestSerializationGitHubManagementFromDict:
    def test_serialization_github_management_user_loaded(self):
        gm = GitHubManagement.from_dict({"user": _user_dict(), "organizations": []})
        assert gm.user.name == "testuser"

    def test_serialization_github_management_organizations_loaded(self):
        gm = GitHubManagement.from_dict({
            "user": _user_dict(),
            "organizations": [_org_dict("OrgA"), _org_dict("OrgB")],
        })
        assert len(gm.organizations) == 2
        assert gm.organizations[0].name == "OrgA"

    def test_serialization_github_management_empty_organizations(self):
        gm = GitHubManagement.from_dict({"user": _user_dict(), "organizations": []})
        assert gm.organizations == []

    def test_serialization_github_management_missing_organizations_key(self):
        gm = GitHubManagement.from_dict({"user": _user_dict()})
        assert gm.organizations == []

class TestSerializationGitHubManagementToDict:
    def test_serialization_github_management_all_keys_present(self):
        gm = GitHubManagement(user=User(name="u"), organizations=[])
        assert set(gm.to_dict().keys()) == {"user", "organizations"}

    def test_serialization_github_management_user_serialized(self):
        gm = GitHubManagement(user=User(name="alice"), organizations=[])
        assert gm.to_dict()["user"]["name"] == "alice"

    def test_serialization_github_management_organizations_serialized(self):
        gm = GitHubManagement(user=User(name="u"),
                              organizations=[Organization(name="OrgA", description="", members=[], teams=[], repositories=[], roles=[])])
        d = gm.to_dict()
        assert d["organizations"][0]["name"] == "OrgA"

class TestSerializationGitHubManagementRoundtrip:
    def test_serialization_github_management_roundtrip_empty(self):
        d = {"user": _user_dict(), "organizations": []}
        assert GitHubManagement.from_dict(d).to_dict() == d

    def test_serialization_github_management_roundtrip_with_orgs(self):
        d = {"user": _user_dict(), "organizations": [_org_dict("OrgA"), _org_dict("OrgB")]}
        assert GitHubManagement.from_dict(d).to_dict() == d

class TestSerializationGitHubManagementYaml:
    def test_serialization_github_management_to_yaml_is_valid_yaml(self):
        gm = GitHubManagement(user=User(name="u"), organizations=[])
        yml = gm.to_yaml()
        parsed = yaml.safe_load(yml)
        assert isinstance(parsed, dict)

    def test_serialization_github_management_from_yaml_basic(self):
        yml = """
user:
  name: testuser
  repositories: []
organizations: []
"""
        gm = GitHubManagement.from_yaml(yml)
        assert gm.user.name == "testuser"
        assert gm.organizations == []

    def test_serialization_github_management_yaml_roundtrip(self):
        gm = GitHubManagement(user=User(name="alice"), organizations=[])
        gm2 = GitHubManagement.from_yaml(gm.to_yaml())
        assert gm2.user.name == "alice"
        assert gm2.organizations == []

    def test_serialization_github_management_from_yaml_loads_actual_file(self, tmp_path):
        yml = tmp_path / "gm.yaml"
        yml.write_text("""
user:
  name: myuser
  repositories: []
organizations:
  - name: SandboxOrg
    description: desc
    members: []
    teams: []
    roles: []
    repositories: []
""")
        from github_management.command.utils import load_github_management_yaml
        gm = load_github_management_yaml(str(yml))
        assert gm.user.name == "myuser"
        assert gm.organizations[0].name == "SandboxOrg"

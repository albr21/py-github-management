from github_management.model.creation.repository.configuration import Configuration
from github_management.model.creation.repository.branch_protection import BranchProtection
from github_management.model.creation.repository.pr_configuration import PRConfiguration

class TestSerializationCreationConfigurationBranchProtectionFromDict:
    def test_serialization_creation_configuration_basic_fields(self):
        bp = BranchProtection.from_dict({
            "branch": "main",
            "required_approving_review_count": 2,
            "require_code_owner_reviews": True,
        })
        assert bp.branch == "main"
        assert bp.required_approving_review_count == 2
        assert bp.require_code_owner_reviews is True

    def test_serialization_creation_configuration_defaults(self):
        bp = BranchProtection.from_dict({"branch": "main"})
        assert bp.required_approving_review_count == 0
        assert bp.require_code_owner_reviews is False

class TestSerializationCreationConfigurationBranchProtectionToDict:
    def test_serialization_creation_configuration_all_keys_present(self):
        bp = BranchProtection(branch="main")
        assert set(bp.to_dict().keys()) == {"branch", "required_approving_review_count", "require_code_owner_reviews"}

class TestSerializationCreationConfigurationBranchProtectionRoundtrip:
    def test_serialization_creation_configuration_roundtrip(self):
        d = {"branch": "main", "required_approving_review_count": 1, "require_code_owner_reviews": True}
        assert BranchProtection.from_dict(d).to_dict() == d

    def test_serialization_creation_configuration_roundtrip_defaults(self):
        d = {"branch": "develop", "required_approving_review_count": 0, "require_code_owner_reviews": False}
        assert BranchProtection.from_dict(d).to_dict() == d

class TestSerializationCreationConfigurationPRConfigurationFromDict:
    def test_serialization_creation_configuration_all_fields(self):
        pr = PRConfiguration.from_dict({
            "allow_merge_commit": True,
            "allow_rebase_merge": True,
            "allow_squash_merge": False,
            "delete_branch_on_merge": False,
            "allow_update_branch": False,
        })
        assert pr.allow_merge_commit is True
        assert pr.allow_rebase_merge is True
        assert pr.allow_squash_merge is False
        assert pr.delete_branch_on_merge is False
        assert pr.allow_update_branch is False

    def test_serialization_creation_configuration_defaults(self):
        pr = PRConfiguration.from_dict({})
        assert pr.allow_merge_commit is False
        assert pr.allow_rebase_merge is False
        assert pr.allow_squash_merge is True
        assert pr.delete_branch_on_merge is True
        assert pr.allow_update_branch is True

class TestSerializationCreationConfigurationPRConfigurationToDict:
    def test_serialization_creation_configuration_all_keys_present(self):
        pr = PRConfiguration()
        assert set(pr.to_dict().keys()) == {
            "allow_merge_commit", "allow_rebase_merge", "allow_squash_merge",
            "delete_branch_on_merge", "allow_update_branch"
        }

class TestSerializationCreationConfigurationPRConfigurationRoundtrip:
    def test_serialization_creation_configuration_roundtrip_defaults(self):
        d = {
            "allow_merge_commit": False,
            "allow_rebase_merge": False,
            "allow_squash_merge": True,
            "delete_branch_on_merge": True,
            "allow_update_branch": True,
        }
        assert PRConfiguration.from_dict(d).to_dict() == d

    def test_serialization_creation_configuration_roundtrip_custom(self):
        d = {
            "allow_merge_commit": True,
            "allow_rebase_merge": True,
            "allow_squash_merge": False,
            "delete_branch_on_merge": False,
            "allow_update_branch": False,
        }
        assert PRConfiguration.from_dict(d).to_dict() == d

def _base_config_dict(**overrides):
    d = {
        "template_repository": "org/template",
        "name": "new-repo",
        "description": "my repo",
        "private": False,
        "has_wiki": False,
        "has_projects": False,
        "include_all_branches": False,
        "branch_protection": None,
        "pr_configuration": None,
    }
    d.update(overrides)
    return d

class TestSerializationCreationConfigurationFromDict:
    def test_serialization_creation_configuration_basic_fields(self):
        c = Configuration.from_dict(_base_config_dict())
        assert c.template_repository == "org/template"
        assert c.name == "new-repo"
        assert c.description == "my repo"
        assert c.private is False

    def test_serialization_creation_configuration_branch_protection_loaded(self):
        bp = {"branch": "main", "required_approving_review_count": 1, "require_code_owner_reviews": False}
        c = Configuration.from_dict(_base_config_dict(branch_protection=bp))
        assert c.branch_protection is not None
        assert c.branch_protection.branch == "main"

    def test_serialization_creation_configuration_pr_configuration_loaded(self):
        pr = {"allow_merge_commit": True, "allow_rebase_merge": False,
               "allow_squash_merge": True, "delete_branch_on_merge": True, "allow_update_branch": True}
        c = Configuration.from_dict(_base_config_dict(pr_configuration=pr))
        assert c.pr_configuration is not None
        assert c.pr_configuration.allow_merge_commit is True

    def test_serialization_creation_configuration_branch_protection_none_when_absent(self):
        c = Configuration.from_dict(_base_config_dict(branch_protection=None))
        assert c.branch_protection is None

    def test_serialization_creation_configuration_private_true(self):
        c = Configuration.from_dict(_base_config_dict(private=True))
        assert c.private is True

    def test_serialization_creation_configuration_has_wiki_true(self):
        c = Configuration.from_dict(_base_config_dict(has_wiki=True))
        assert c.has_wiki is True

class TestSerializationCreationConfigurationToDict:
    def test_serialization_creation_configuration_all_keys_present(self):
        c = Configuration(template_repository="tmpl", name="repo")
        keys = set(c.to_dict().keys())
        expected = {"template_repository", "name", "description", "private", "has_wiki",
                    "has_projects", "include_all_branches", "branch_protection", "pr_configuration"}
        assert keys == expected

    def test_serialization_creation_configuration_branch_protection_none_stored_as_none(self):
        c = Configuration(template_repository="t", name="r", branch_protection=None)
        assert c.to_dict()["branch_protection"] is None

    def test_serialization_creation_configuration_pr_configuration_serialized(self):
        pr = PRConfiguration()
        c = Configuration(template_repository="t", name="r", pr_configuration=pr)
        d = c.to_dict()
        assert isinstance(d["pr_configuration"], dict)

class TestSerializationCreationConfigurationRoundtrip:
    def test_serialization_creation_configuration_roundtrip_minimal(self):
        d = _base_config_dict()
        assert Configuration.from_dict(d).to_dict() == d

    def test_serialization_creation_configuration_roundtrip_with_branch_protection(self):
        bp = {"branch": "main", "required_approving_review_count": 2, "require_code_owner_reviews": True}
        d = _base_config_dict(branch_protection=bp)
        assert Configuration.from_dict(d).to_dict() == d

    def test_serialization_creation_configuration_roundtrip_with_pr_configuration(self):
        pr = {"allow_merge_commit": False, "allow_rebase_merge": False, "allow_squash_merge": True,
              "delete_branch_on_merge": True, "allow_update_branch": True}
        d = _base_config_dict(pr_configuration=pr)
        assert Configuration.from_dict(d).to_dict() == d

    def test_serialization_creation_configuration_from_yaml_roundtrip(self):
        import yaml
        d = _base_config_dict(name="yaml-repo", private=True)
        yml = yaml.dump(d)
        c = Configuration.from_yaml(yml)
        assert c.name == "yaml-repo"
        assert c.private is True

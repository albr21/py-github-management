import pytest
from github_management.command.utils import _match_filter, load_github_management_yaml, load_repository_creation_config_yaml, save

class TestCommandMatchFilter:
    def test_command_none_pattern_always_matches(self):
        assert _match_filter("anything", None) is True

    def test_command_none_pattern_matches_empty_string(self):
        assert _match_filter("", None) is True

    def test_command_exact_match(self):
        assert _match_filter("repository_1", "repository_1") is True

    def test_command_exact_no_match(self):
        assert _match_filter("repository_2", "repository_1") is False

    def test_command_wildcard_star_matches_suffix(self):
        assert _match_filter("repo_abc", "repo_*") is True

    def test_command_wildcard_star_does_not_match_different_prefix(self):
        assert _match_filter("other_abc", "repo_*") is False

    def test_command_wildcard_star_matches_exactly(self):
        assert _match_filter("repo_", "repo_*") is True

    def test_command_wildcard_question_mark(self):
        assert _match_filter("repo1", "repo?") is True

    def test_command_wildcard_question_mark_no_match_longer(self):
        assert _match_filter("repo12", "repo?") is False

    def test_command_star_only_matches_any(self):
        assert _match_filter("anything_here_123", "*") is True

    def test_command_star_only_matches_empty(self):
        assert _match_filter("", "*") is True

    def test_command_prefix_and_suffix_wildcard(self):
        assert _match_filter("start_middle_end", "start_*_end") is True

    def test_command_prefix_and_suffix_wildcard_no_match(self):
        assert _match_filter("different_middle_end", "start_*_end") is False

class TestCommandLoadGitHubManagementYaml:
    def test_command_loads_valid_yaml(self, tmp_path):
        yml = tmp_path / "gm.yaml"
        yml.write_text("""
user:
  name: myuser
  repositories: []
organizations: []
""")
        gm = load_github_management_yaml(str(yml))
        assert gm.user.name == "myuser"
        assert gm.organizations == []

    def test_command_loads_yaml_with_org(self, tmp_path):
        yml = tmp_path / "gm.yaml"
        yml.write_text("""
user:
  name: myuser
  repositories: []
organizations:
  - name: SandboxOrg
    description: test
    members: []
    teams: []
    roles: []
    repositories: []
""")
        gm = load_github_management_yaml(str(yml))
        assert len(gm.organizations) == 1
        assert gm.organizations[0].name == "SandboxOrg"

    def test_command_invalid_file_path_raises(self):
        with pytest.raises(FileNotFoundError):
            load_github_management_yaml("/nonexistent/path/file.yaml")


class TestCommandLoadRepositoryCreationConfigYaml:
    def test_command_loads_repository_creation_config_yaml(self, tmp_path):
        yml = tmp_path / "repo-config.yaml"
        yml.write_text("""
template_repository: org/template
name: new-repo
description: created from template
private: true
has_wiki: true
has_projects: false
include_all_branches: true
branch_protection:
  branch: main
  required_approving_review_count: 2
  require_code_owner_reviews: true
pr_configuration:
  allow_merge_commit: true
  allow_rebase_merge: false
  allow_squash_merge: true
  delete_branch_on_merge: true
  allow_update_branch: false
""")
        config = load_repository_creation_config_yaml(str(yml))
        assert config.template_repository == "org/template"
        assert config.name == "new-repo"
        assert config.branch_protection is not None
        assert config.pr_configuration is not None

class TestCommandSave:
    def test_command_saves_content_to_file(self, tmp_path):
        f = tmp_path / "output.txt"
        save(str(f), "hello world")
        assert f.read_text() == "hello world"

    def test_command_overwrites_existing_file(self, tmp_path):
        f = tmp_path / "output.txt"
        f.write_text("old content")
        save(str(f), "new content")
        assert f.read_text() == "new content"

    def test_command_saves_empty_string(self, tmp_path):
        f = tmp_path / "output.txt"
        save(str(f), "")
        assert f.read_text() == ""

    def test_command_saves_yaml_content(self, tmp_path):
        f = tmp_path / "output.yaml"
        save(str(f), "key: value\n")
        assert "key: value" in f.read_text()

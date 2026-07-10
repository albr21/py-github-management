from types import SimpleNamespace
from unittest.mock import Mock

from github_management.model.creation.repository.pr_configuration import PRConfiguration


class TestCreationPRConfigurationApply:
    def test_creation_pr_configuration_apply_edits_repository(self):
        github_repository = SimpleNamespace(edit=Mock())
        configuration = PRConfiguration(
            allow_merge_commit=True,
            allow_rebase_merge=True,
            allow_squash_merge=False,
            delete_branch_on_merge=False,
            allow_update_branch=False,
        )

        configuration.apply(github_repository)

        github_repository.edit.assert_called_once_with(
            allow_merge_commit=True,
            allow_rebase_merge=True,
            allow_squash_merge=False,
            delete_branch_on_merge=False,
            allow_update_branch=False,
        )

class TestCreationPRConfigurationStr:
    def test_creation_pr_configuration_str_returns_formatted_fields(self):
        configuration = PRConfiguration(
            allow_merge_commit=True,
            allow_rebase_merge=False,
            allow_squash_merge=True,
            delete_branch_on_merge=True,
            allow_update_branch=False,
        )

        assert "PRConfiguration(" in str(configuration)
        assert "allow_merge_commit=True" in str(configuration)

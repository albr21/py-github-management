import pytest
from types import SimpleNamespace
from unittest.mock import Mock

from github.GithubException import UnknownObjectException

from github_management.model.creation.repository.branch_protection import BranchProtection


class TestCreationBranchProtectionApply:
    def test_creation_branch_protection_apply_sets_protection(self):
        edit_protection = Mock()
        github_branch = SimpleNamespace(edit_protection=edit_protection)
        github_repository = SimpleNamespace(full_name="org/repo", get_branch=lambda branch: github_branch)

        protection = BranchProtection(
            branch="main",
            required_approving_review_count=2,
            require_code_owner_reviews=True,
        )

        protection.apply(github_repository)

        edit_protection.assert_called_once_with(
            required_approving_review_count=2,
            require_code_owner_reviews=True,
        )

    def test_creation_branch_protection_retries_on_missing_branch(self, monkeypatch):
        edit_protection = Mock()
        github_branch = SimpleNamespace(edit_protection=edit_protection)
        attempts = {"count": 0}

        def get_branch(branch_name):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise UnknownObjectException(status=404, data={})
            return github_branch

        github_repository = SimpleNamespace(full_name="org/repo", get_branch=get_branch)
        protection = BranchProtection(branch="main", required_approving_review_count=1, require_code_owner_reviews=False)
        protection._request_retries = 2
        monkeypatch.setattr("github_management.model.creation.repository.branch_protection.time.sleep", lambda seconds: None)

        protection.apply(github_repository)

        assert attempts["count"] == 2
        edit_protection.assert_called_once_with(
            required_approving_review_count=1,
            require_code_owner_reviews=False,
        )

    def test_creation_branch_protection_raises_after_final_retry(self, monkeypatch):
        def get_branch(branch_name):
            raise UnknownObjectException(status=404, data={})

        github_repository = SimpleNamespace(full_name="org/repo", get_branch=get_branch)
        protection = BranchProtection(branch="main")
        protection._request_retries = 1
        monkeypatch.setattr("github_management.model.creation.repository.branch_protection.time.sleep", lambda seconds: None)

        with pytest.raises(UnknownObjectException):
            protection.apply(github_repository)

class TestCreationBranchProtectionStr:
    def test_creation_branch_protection_str_returns_formatted_fields(self):
        protection = BranchProtection(branch="main", required_approving_review_count=2, require_code_owner_reviews=True)

        assert str(protection) == "BranchProtection(branch='main', required_approving_review_count=2, require_code_owner_reviews=True)"

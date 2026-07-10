import time
from dataclasses import dataclass
from github.Repository import Repository as GitHubRepository
from github.GithubException import UnknownObjectException

@dataclass
class BranchProtection:
    """
    Branch protection configuration for a branch.
    """

    branch: str
    required_approving_review_count: int = 0
    require_code_owner_reviews: bool = False
    _request_delay: int = 3
    _request_retries: int = 5

    def to_dict(self) -> dict:
        return {
            "branch": self.branch,
            "required_approving_review_count": self.required_approving_review_count,
            "require_code_owner_reviews": self.require_code_owner_reviews
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BranchProtection":
        branch = data.get("branch", "")
        required_approving_review_count = data.get("required_approving_review_count", 0)
        require_code_owner_reviews = data.get("require_code_owner_reviews", False)

        return cls(
            branch=branch,
            required_approving_review_count=required_approving_review_count,
            require_code_owner_reviews=require_code_owner_reviews
        )

    def __str__(self):
        """
        String representation of the object
        """
        kv = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{self.__class__.__name__}({kv})"

    def apply(self, github_repository: GitHubRepository) -> None:
        """
        Apply the branch protection rules to the specified repository.
        """

        for attempt in range(self._request_retries):
            try:
                github_branch = github_repository.get_branch(self.branch)
                break
            except UnknownObjectException as e:
                if attempt < self._request_retries - 1:
                    # pylint: disable=C0301
                    print(f"Branch '{self.branch}' not found in repository '{github_repository.full_name}'. Retrying ({attempt + 1}/{self._request_retries})...")
                    # pylint: enable=C0301
                    time.sleep(self._request_delay)
                else:
                    raise e

        github_branch.edit_protection(
            required_approving_review_count=self.required_approving_review_count,
            require_code_owner_reviews=self.require_code_owner_reviews
        )

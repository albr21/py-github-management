from dataclasses import dataclass
from github.Repository import Repository as GitHubRepository

@dataclass
class PRConfiguration:
    """
    Pull request configuration
    """
    allow_merge_commit: bool = False
    allow_rebase_merge: bool = False
    allow_squash_merge: bool = True
    delete_branch_on_merge: bool = True
    allow_update_branch: bool = True

    def to_dict(self) -> dict:
        return {
            "allow_merge_commit": self.allow_merge_commit,
            "allow_rebase_merge": self.allow_rebase_merge,
            "allow_squash_merge": self.allow_squash_merge,
            "delete_branch_on_merge": self.delete_branch_on_merge,
            "allow_update_branch": self.allow_update_branch
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PRConfiguration":
        allow_merge_commit = data.get("allow_merge_commit", False)
        allow_rebase_merge = data.get("allow_rebase_merge", False)
        allow_squash_merge = data.get("allow_squash_merge", True)
        delete_branch_on_merge = data.get("delete_branch_on_merge", True)
        allow_update_branch = data.get("allow_update_branch", True)

        return cls(
            allow_merge_commit=allow_merge_commit,
            allow_rebase_merge=allow_rebase_merge,
            allow_squash_merge=allow_squash_merge,
            delete_branch_on_merge=delete_branch_on_merge,
            allow_update_branch=allow_update_branch
        )

    def __str__(self):
        """
        String representation of the object
        """
        kv = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{self.__class__.__name__}({kv})"

    def apply(self, github_repository: GitHubRepository) -> None:
        """
        Apply the pull request configuration to the specified repository.
        """
        github_repository.edit(
            allow_merge_commit=self.allow_merge_commit,
            allow_rebase_merge=self.allow_rebase_merge,
            allow_squash_merge=self.allow_squash_merge,
            delete_branch_on_merge=self.delete_branch_on_merge,
            allow_update_branch=self.allow_update_branch
        )

from .github_object import GitHubObject
from .base_role import BaseRole
from ...model.diff.change import Change
from ...model.diff.change_type import ChangeType
from ...model.diff.utils import diff_set

class Role(GitHubObject):
    """
    Class representing a GitHub role
    """

    # @param name [str]: Name of the role
    # @param description [str]: Description of the role
    # @param permissions [List[str] | None]: List of permissions associated with the role
    # @param base_role [str | None]: Base role (e.g., read, triage, write, maintain, admin)
    #                                that this custom role extends, if any
    def __init__(
            self,
            *,
            name: str,
            description: str = "",
            permissions: list[str] = None,
            base_role: BaseRole | None = None
        ) -> None:

        self.name = name
        self.description = description
        self.permissions = permissions if permissions is not None else []
        self.base_role = base_role

    @classmethod
    def from_dict(cls, data: dict) -> "Role":
        role_value = data.get("base_role")
        if role_value is not None:
            base_role = BaseRole(role_value)
        else:
            base_role = None
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            permissions=data.get("permissions", []),
            base_role=base_role
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "base_role": self.base_role.value if self.base_role else None
        }

    def diff(self, other: "Role", path: str = "") -> list[Change]:
        changes: list[Change] = []
        if self.description != other.description:
            changes.append(Change(f"{path}.description", ChangeType.CHANGED, self.description, other.description))
        local_base = self.base_role.value if self.base_role else None
        remote_base = other.base_role.value if other.base_role else None
        if local_base != remote_base:
            changes.append(Change(f"{path}.base_role", ChangeType.CHANGED, local_base, remote_base))
        changes.extend(diff_set(self.permissions, other.permissions, f"{path}.permissions"))
        return changes

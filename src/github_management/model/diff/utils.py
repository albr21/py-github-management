from .change import Change
from .change_type import ChangeType

def diff_list_by_name(local_items: list, remote_items: list, path: str, *, key: str = "name") -> list[Change]:
    """
    Compare two lists of GitHubObject that have a `name` (or other key) attribute.
    Each item must implement diff(other, path) -> list[Change].
    """
    changes: list[Change] = []

    local_by_key = {getattr(item, key): item for item in local_items if item is not None}
    remote_by_key = {getattr(item, key): item for item in remote_items if item is not None}

    for name in sorted(set(local_by_key) | set(remote_by_key)):
        item_path = f"{path}[{name}]"
        if name not in remote_by_key:
            changes.append(Change(item_path, ChangeType.ADDED, local_by_key[name], None))
        elif name not in local_by_key:
            changes.append(Change(item_path, ChangeType.REMOVED, None, remote_by_key[name]))
        else:
            changes.extend(local_by_key[name].diff(remote_by_key[name], item_path))

    return changes

def diff_list_by_login(local_items: list, remote_items: list, path: str) -> list[Change]:
    """
    Compare two lists of GitHubObject that have a `login` attribute (e.g. Member).
    """
    return diff_list_by_name(local_items, remote_items, path, key="login")

def diff_set(local_items: list[str], remote_items: list[str], path: str) -> list[Change]:
    """Compare two simple lists of strings (e.g. topics, team member logins)."""
    changes: list[Change] = []
    local_set = set(local_items)
    remote_set = set(remote_items)

    for item in sorted(local_set - remote_set):
        changes.append(Change(path, ChangeType.ADDED, item, None))
    for item in sorted(remote_set - local_set):
        changes.append(Change(path, ChangeType.REMOVED, None, item))

    return changes

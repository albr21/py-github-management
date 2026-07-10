import fnmatch
from ..model.github.github_management import GitHubManagement
from ..model.creation.repository.configuration import Configuration as RepositoryConfiguration

def load_github_management_yaml(file_path: str) -> GitHubManagement:
    """
    Load a GitHubManagement instance from a YAML file.
    """

    f = open(file_path, "r", encoding="utf-8")
    content = f.read()
    f.close()
    github_management = GitHubManagement.from_yaml(content)
    return github_management

def load_repository_creation_config_yaml(file_path: str) -> RepositoryConfiguration:
    """
    Load a RepositoryConfiguration instance from a YAML file.
    """

    f = open(file_path, "r", encoding="utf-8")
    content = f.read()
    f.close()
    repository_creation_config = RepositoryConfiguration.from_yaml(content)
    return repository_creation_config

def save(file_path: str, content: str) -> None:
    """
    Save content to a file.
    """
    f = open(file_path, "w", encoding="utf-8")
    f.write(content)
    f.close()

def _match_filter(name: str, pattern: str | None) -> bool:
    """Return True if name matches the wildcard pattern (or if pattern is None)."""
    if pattern is None:
        return True
    return fnmatch.fnmatch(name, pattern)

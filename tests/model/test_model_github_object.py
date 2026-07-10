import pytest
from github_management.model.github.github_object import GitHubObject

class DummyGitHubObject(GitHubObject):
    def __init__(self, value: str = "value") -> None:
        self.value = value

    def to_dict(self) -> dict:
        return {"value": self.value}

    def diff(self, other: "GitHubObject", path: str = "") -> list:
        return []

class TestModelGitHubObjectBase:
    def test_model_base_methods_raise_not_implemented(self):
        with pytest.raises(NotImplementedError):
            GitHubObject.from_dict({})

        dummy = DummyGitHubObject("x")

        assert str(dummy) == "DummyGitHubObject(value='x')"

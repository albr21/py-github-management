from abc import ABC, abstractmethod

class GitHubObject(ABC):
    @classmethod
    def from_github_object(cls, github_object: object) -> "GitHubObject":
        """
        Build from an already-fetched PyGithub object.
        No API call. Override in subclasses if needed.
        """
        raise NotImplementedError(f"{cls.__name__} does not implement from_github_object()")

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        """

    @classmethod
    def from_dict(cls, data: dict) -> "GitHubObject":
        """
        Create an instance of the object from a dictionary representation.
        """
        raise NotImplementedError(f"{cls.__name__} does not implement from_dict()")

    @abstractmethod
    def diff(self, other: "GitHubObject", path: str = "") -> list:
        """
        Compare self (local) against other (remote) and return a list of Change.
        """

    def __str__(self):
        """
        String representation of the object
        """
        kv = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{self.__class__.__name__}({kv})"

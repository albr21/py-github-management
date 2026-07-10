import sys
from os import environ
from github import Auth, Github, GithubException

class Client():
    """
    GitHub Client
    """

    def __init__(self, *, base_url: str) -> None:
        self.base_url = base_url
        self.__login()

    def __login(self) -> None:
        self.token = environ.get("GITHUB_TOKEN")
        try:
            auth = Auth.Token(self.token)
            self.client = Github(auth=auth, base_url=self.base_url)
        except GithubException as e:
            print(f"GitHub API error: {e}")
            sys.exit(1)
        except AssertionError as e:
            print(f"Error authenticating with GitHub API: {e}")
            sys.exit(1)
        else:
            login = self.client.get_user().login
            print(f"Successfully authenticated with GitHub API as {login}")

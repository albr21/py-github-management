import pytest
from types import SimpleNamespace

import github_management.client as client_module
from github_management.client import Client

class TestModelClientLogin:
    def test_model_client_login_uses_token_and_prints_success(self, monkeypatch, capsys):
        monkeypatch.setenv("GITHUB_TOKEN", "secret-token")

        class FakeGithub:
            def __init__(self, auth, base_url):
                self.auth = auth
                self.base_url = base_url

            def get_user(self):
                return SimpleNamespace(login="octocat")

        monkeypatch.setattr(client_module.Auth, "Token", lambda token: f"token:{token}")
        monkeypatch.setattr(client_module, "Github", FakeGithub)

        client = Client(base_url="https://example.test")

        assert client.token == "secret-token"
        assert client.client.base_url == "https://example.test"
        assert "Successfully authenticated with GitHub API as octocat" in capsys.readouterr().out

    def test_model_client_login_exits_on_github_exception(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "secret-token")

        class FakeGithub:
            def __init__(self, auth, base_url):
                raise client_module.GithubException(status=401, data={})

        monkeypatch.setattr(client_module.Auth, "Token", lambda token: f"token:{token}")
        monkeypatch.setattr(client_module, "Github", FakeGithub)

        with pytest.raises(SystemExit):
            Client(base_url="https://example.test")

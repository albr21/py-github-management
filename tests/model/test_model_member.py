from types import SimpleNamespace

from github_management.model.github.member import Member

class TestModelMemberFetchFromGitHub:
    def test_model_member_fetch_from_github_returns_member_with_login_and_name(self):
        class FakeClient:
            client = SimpleNamespace(get_user=lambda login: SimpleNamespace(name="Alice"))

        member = Member.fetch_from_github(FakeClient(), "alice")

        assert member.login == "alice"
        assert member.name == "Alice"

class TestModelMemberFromGitHubObject:
    def test_model_member_from_github_object_maps_login_and_name(self):
        github_object = SimpleNamespace(login="alice", name="Alice")

        member = Member.from_github_object(github_object)

        assert member.login == "alice"
        assert member.name == "Alice"

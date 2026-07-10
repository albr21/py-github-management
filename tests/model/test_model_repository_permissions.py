from types import SimpleNamespace

from github.GithubException import UnknownObjectException

from github_management.model.github.repository_permissions import RepositoryPermissions

def _permission_flags(*, admin=False, maintain=False, push=False, triage=False, pull=False):
    return SimpleNamespace(admin=admin, maintain=maintain, push=push, triage=triage, pull=pull)

def _make_permissions(*, admin=None, maintain=None, write=None, triage=None, read=None):
    return RepositoryPermissions(
        admin=admin or [],
        maintain=maintain or [],
        write=write or [],
        triage=triage or [],
        read=read or [],
    )

class TestModelRepositoryPermissionsAllLogins:
    def test_model_all_logins_empty_permissions_returns_empty_list(self):
        p = _make_permissions()
        assert p.all_logins() == []

    def test_model_all_logins_single_admin(self):
        p = _make_permissions(admin=["alice"])
        assert p.all_logins() == ["alice"]

    def test_model_all_logins_combines_all_levels(self):
        p = _make_permissions(admin=["a"], maintain=["b"], write=["c"], triage=["d"], read=["e"])
        assert p.all_logins() == ["a", "b", "c", "d", "e"]

    def test_model_all_logins_preserves_order_admin_first(self):
        p = _make_permissions(admin=["admin1", "admin2"], read=["reader1"])
        logins = p.all_logins()
        assert logins.index("admin1") < logins.index("reader1")

    def test_model_all_logins_multiple_per_level(self):
        p = _make_permissions(write=["alice", "bob"], read=["carol"])
        assert p.all_logins() == ["alice", "bob", "carol"]

class TestModelRepositoryPermissionsFromGitHubObject:
    def test_model_repository_permissions_collects_user_and_team_permissions(self):
        collaborators = [
            SimpleNamespace(login="alice", permissions=_permission_flags(admin=True)),
            SimpleNamespace(login="bob", permissions=_permission_flags(maintain=True)),
            SimpleNamespace(login="carol", permissions=_permission_flags(push=True)),
            SimpleNamespace(login="dave", permissions=_permission_flags(triage=True)),
            SimpleNamespace(login="eve", permissions=_permission_flags(pull=True)),
        ]
        teams = [
            SimpleNamespace(name="team-admin", permissions=_permission_flags(admin=True)),
            SimpleNamespace(name="team-maintain", permissions=_permission_flags(maintain=True)),
            SimpleNamespace(name="team-write", permissions=_permission_flags(push=True)),
            SimpleNamespace(name="team-triage", permissions=_permission_flags(triage=True)),
            SimpleNamespace(name="team-read", permissions=_permission_flags(pull=True)),
        ]

        class FakeRepository:
            full_name = "org/repo"

            def get_collaborators(self):
                return collaborators

            def get_teams(self):
                return teams

        permissions = RepositoryPermissions.from_github_object(FakeRepository())

        assert permissions.admin == ["alice", "team-admin"]
        assert permissions.maintain == ["bob", "team-maintain"]
        assert permissions.write == ["carol", "team-write"]
        assert permissions.triage == ["dave", "team-triage"]
        assert permissions.read == ["eve", "team-read"]

    def test_model_repository_permissions_ignores_missing_teams(self):
        collaborators = [SimpleNamespace(login="alice", permissions=_permission_flags(admin=True))]

        class FakeRepository:
            full_name = "org/repo"

            def get_collaborators(self):
                return collaborators

            def get_teams(self):
                raise UnknownObjectException(status=404, data={})

        permissions = RepositoryPermissions.from_github_object(FakeRepository())

        assert permissions.admin == ["alice"]
        assert permissions.maintain == []
        assert permissions.write == []
        assert permissions.triage == []
        assert permissions.read == []

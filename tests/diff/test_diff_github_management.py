from github_management.model.github.github_management import GitHubManagement
from github_management.model.github.organization import Organization
from github_management.model.github.user import User
from github_management.model.diff.change_type import ChangeType
from github_management.model.diff.change_report import ChangeReport

def _user(name="testuser"):
    return User(name=name)

def _org(name, description=""):
    return Organization(name=name, description=description)

def _make_gm(orgs=None, user_name="testuser"):
    return GitHubManagement(user=_user(user_name), organizations=orgs or [])

class TestDiffGitHubManagementIdentical:
    def test_diff_no_orgs_no_changes(self):
        gm = _make_gm()
        report = gm.diff(gm)
        assert not report.has_changes()

    def test_diff_same_orgs_no_changes(self):
        gm = _make_gm(orgs=[_org("OrgA"), _org("OrgB")])
        report = gm.diff(gm)
        assert not report.has_changes()

class TestDiffGitHubManagementOrgAdded:
    def test_diff_org_added_in_local(self):
        local = _make_gm(orgs=[_org("OrgA"), _org("OrgNew")])
        remote = _make_gm(orgs=[_org("OrgA")])
        report = local.diff(remote)
        assert report.has_changes()
        assert any(c.type == ChangeType.ADDED for c in report.changes)

    def test_diff_added_org_path_contains_name(self):
        local = _make_gm(orgs=[_org("OrgNew")])
        remote = _make_gm(orgs=[])
        report = local.diff(remote)
        assert any("OrgNew" in c.path for c in report.changes)

class TestDiffGitHubManagementOrgRemoved:
    def test_diff_org_removed(self):
        local = _make_gm(orgs=[])
        remote = _make_gm(orgs=[_org("OrgGone")])
        report = local.diff(remote)
        assert report.has_changes()
        assert any(c.type == ChangeType.REMOVED for c in report.changes)

    def test_diff_removed_org_path_contains_name(self):
        local = _make_gm(orgs=[])
        remote = _make_gm(orgs=[_org("OrgGone")])
        report = local.diff(remote)
        assert any("OrgGone" in c.path for c in report.changes)

class TestDiffGitHubManagementOrgDescriptionChanged:
    def test_diff_org_description_change_detected(self):
        local = _make_gm(orgs=[_org("OrgA", description="new")])
        remote = _make_gm(orgs=[_org("OrgA", description="old")])
        report = local.diff(remote)
        assert report.has_changes()
        assert any(c.type == ChangeType.CHANGED for c in report.changes)

class TestDiffGitHubManagementMultipleOrgs:
    def test_diff_one_added_one_removed(self):
        local = _make_gm(orgs=[_org("OrgA"), _org("OrgNew")])
        remote = _make_gm(orgs=[_org("OrgA"), _org("OrgOld")])
        report = local.diff(remote)
        types = {c.type for c in report.changes}
        assert ChangeType.ADDED in types
        assert ChangeType.REMOVED in types

    def test_diff_multiple_changes_count(self):
        local = _make_gm(orgs=[_org("OrgA", description="new"), _org("OrgB")])
        remote = _make_gm(orgs=[_org("OrgA", description="old"), _org("OrgB")])
        report = local.diff(remote)
        assert len(report.changes) == 1

class TestDiffGitHubManagementChangeReport:
    def test_diff_report_is_change_report_type(self):
        gm = _make_gm()
        assert isinstance(gm.diff(gm), ChangeReport)

    def test_diff_no_changes_report_str_contains_no_differences(self):
        gm = _make_gm()
        assert "No differences found." in str(gm.diff(gm))

    def test_diff_with_changes_report_str_contains_count(self):
        local = _make_gm(orgs=[_org("OrgNew")])
        remote = _make_gm(orgs=[])
        report = local.diff(remote)
        assert "difference(s)" in str(report)

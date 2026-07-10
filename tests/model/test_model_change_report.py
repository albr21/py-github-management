from github_management.model.diff.change import Change
from github_management.model.diff.change_report import ChangeReport
from github_management.model.diff.change_type import ChangeType
from github_management.model.diff.color import Color

def _make_change(path="x", ct=ChangeType.ADDED, local="l", remote=None):
    return Change(path=path, type=ct, local=local, remote=remote)

class TestModelChangeReportHasChanges:
    def test_model_empty_list_has_no_changes(self):
        report = ChangeReport(changes=[])
        assert report.has_changes() is False

    def test_model_single_change_has_changes(self):
        report = ChangeReport(changes=[_make_change()])
        assert report.has_changes() is True

    def test_model_multiple_changes_has_changes(self):
        report = ChangeReport(changes=[_make_change(), _make_change(path="y")])
        assert report.has_changes() is True

class TestModelChangeReportStrNoChanges:
    def test_model_no_changes_contains_no_differences(self):
        report = ChangeReport(changes=[])
        s = str(report)
        assert "No differences found." in s

    def test_model_no_changes_starts_with_green(self):
        report = ChangeReport(changes=[])
        assert str(report).startswith(Color.GREEN)

class TestModelChangeReportStrWithChanges:
    def test_model_single_change_count_in_report(self):
        report = ChangeReport(changes=[_make_change()])
        assert "1 difference(s)" in str(report)

    def test_model_three_changes_count_in_report(self):
        changes = [_make_change(path=f"p{i}") for i in range(3)]
        report = ChangeReport(changes=changes)
        assert "3 difference(s)" in str(report)

    def test_model_report_contains_each_change_path(self):
        c1 = _make_change(path="alpha")
        c2 = _make_change(path="beta", ct=ChangeType.REMOVED, local=None, remote="r")
        report = ChangeReport(changes=[c1, c2])
        s = str(report)
        assert "alpha" in s
        assert "beta" in s

    def test_model_report_starts_with_yellow(self):
        report = ChangeReport(changes=[_make_change()])
        assert str(report).startswith(Color.YELLOW)

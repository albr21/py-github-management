from github_management.model.diff.change import Change
from github_management.model.diff.change_type import ChangeType
from github_management.model.diff.color import Color

class TestModelChangeConstruction:
    def test_model_attributes_stored(self):
        c = Change(path="orgs[Foo].name", type=ChangeType.CHANGED, local="new", remote="old")
        assert c.path == "orgs[Foo].name"
        assert c.type == ChangeType.CHANGED
        assert c.local == "new"
        assert c.remote == "old"

    def test_model_local_can_be_none(self):
        c = Change(path="x", type=ChangeType.REMOVED, local=None, remote="old")
        assert c.local is None

    def test_model_remote_can_be_none(self):
        c = Change(path="x", type=ChangeType.ADDED, local="new", remote=None)
        assert c.remote is None

class TestModelChangeStrAdded:
    """Change of type ADDED should render in green with '+'."""

    def test_model_contains_plus_prefix(self):
        c = Change(path="repos.topics", type=ChangeType.ADDED, local="ml", remote=None)
        s = str(c)
        assert "+ repos.topics: ml" in s

    def test_model_starts_with_green(self):
        c = Change(path="p", type=ChangeType.ADDED, local="v", remote=None)
        assert str(c).startswith(Color.GREEN)

    def test_model_ends_with_reset(self):
        c = Change(path="p", type=ChangeType.ADDED, local="v", remote=None)
        assert str(c).endswith(Color.RESET)

    def test_model_does_not_contain_remote(self):
        c = Change(path="p", type=ChangeType.ADDED, local="new_val", remote=None)
        assert "None" not in str(c)

class TestModelChangeStrRemoved:
    """Change of type REMOVED should render in red with '-'."""

    def test_model_contains_minus_prefix(self):
        c = Change(path="repos.topics", type=ChangeType.REMOVED, local=None, remote="ml")
        s = str(c)
        assert "- repos.topics: ml" in s

    def test_model_starts_with_red(self):
        c = Change(path="p", type=ChangeType.REMOVED, local=None, remote="v")
        assert str(c).startswith(Color.RED)

    def test_model_ends_with_reset(self):
        c = Change(path="p", type=ChangeType.REMOVED, local=None, remote="v")
        assert str(c).endswith(Color.RESET)

class TestModelChangeStrChanged:
    """Change of type CHANGED should render in yellow showing both local and remote."""

    def test_model_contains_tilde_prefix(self):
        c = Change(path="desc", type=ChangeType.CHANGED, local="new_desc", remote="old_desc")
        s = str(c)
        assert "~ desc:" in s

    def test_model_contains_remote_value(self):
        c = Change(path="desc", type=ChangeType.CHANGED, local="new_desc", remote="old_desc")
        assert "old_desc" in str(c)

    def test_model_contains_local_value(self):
        c = Change(path="desc", type=ChangeType.CHANGED, local="new_desc", remote="old_desc")
        assert "new_desc" in str(c)

    def test_model_contains_remote_label(self):
        c = Change(path="desc", type=ChangeType.CHANGED, local="n", remote="o")
        assert "remote:" in str(c)

    def test_model_contains_local_label(self):
        c = Change(path="desc", type=ChangeType.CHANGED, local="n", remote="o")
        assert "local:" in str(c)

    def test_model_starts_with_yellow(self):
        c = Change(path="p", type=ChangeType.CHANGED, local="n", remote="o")
        assert str(c).startswith(Color.YELLOW)

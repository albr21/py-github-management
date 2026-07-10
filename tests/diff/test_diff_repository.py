from github_management.model.github.repository import Repository
from github_management.model.github.repository_visibility import RepositoryVisibility
from github_management.model.github.repository_permissions import RepositoryPermissions
from github_management.model.diff.change_type import ChangeType

def _make_repo(**kwargs):
    defaults = dict(
        name="repo1",
        owner="org1",
        description="desc",
        archive=False,
        visibility=RepositoryVisibility.PUBLIC,
        topics=[],
        permissions=None,
    )
    defaults.update(kwargs)
    return Repository(**defaults)

class TestDiffRepositoryIdentical:
    def test_diff_all_same_no_changes(self):
        r = _make_repo()
        assert r.diff(r, "path") == []

    def test_diff_same_with_topics_no_changes(self):
        r = _make_repo(topics=["python", "ml"])
        assert r.diff(r, "path") == []

class TestDiffRepositoryOwnerChanged:
    def test_diff_owner_change_produces_change(self):
        local = _make_repo(owner="org_new")
        remote = _make_repo(owner="org_old")
        result = local.diff(remote, "path")
        owner_changes = [c for c in result if "owner" in c.path]
        assert len(owner_changes) == 1
        assert owner_changes[0].type == ChangeType.CHANGED
        assert owner_changes[0].local == "org_new"
        assert owner_changes[0].remote == "org_old"

class TestDiffRepositoryDescriptionChanged:
    def test_diff_description_change(self):
        local = _make_repo(description="new desc")
        remote = _make_repo(description="old desc")
        result = local.diff(remote, "path")
        desc_changes = [c for c in result if "description" in c.path]
        assert len(desc_changes) == 1
        assert desc_changes[0].type == ChangeType.CHANGED

    def test_diff_description_change_to_empty(self):
        local = _make_repo(description="")
        remote = _make_repo(description="was something")
        result = local.diff(remote, "path")
        assert any("description" in c.path for c in result)

    def test_diff_description_no_change(self):
        r = _make_repo(description="same desc")
        assert r.diff(r, "path") == []

class TestDiffRepositoryArchiveChanged:
    def test_diff_archive_true_to_false(self):
        local = _make_repo(archive=False)
        remote = _make_repo(archive=True)
        result = local.diff(remote, "path")
        archive_changes = [c for c in result if "archive" in c.path]
        assert len(archive_changes) == 1
        assert archive_changes[0].local is False
        assert archive_changes[0].remote is True

    def test_diff_archive_false_to_true(self):
        local = _make_repo(archive=True)
        remote = _make_repo(archive=False)
        result = local.diff(remote, "path")
        assert any("archive" in c.path for c in result)

    def test_diff_archive_same_no_change(self):
        local = _make_repo(archive=True)
        remote = _make_repo(archive=True)
        assert not any("archive" in c.path for c in local.diff(remote, "path"))

class TestDiffRepositoryVisibilityChanged:
    def test_diff_public_to_private(self):
        local = _make_repo(visibility=RepositoryVisibility.PRIVATE)
        remote = _make_repo(visibility=RepositoryVisibility.PUBLIC)
        result = local.diff(remote, "path")
        vis_changes = [c for c in result if "visibility" in c.path]
        assert len(vis_changes) == 1
        assert vis_changes[0].local == "private"
        assert vis_changes[0].remote == "public"

    def test_diff_private_to_internal(self):
        local = _make_repo(visibility=RepositoryVisibility.INTERNAL)
        remote = _make_repo(visibility=RepositoryVisibility.PRIVATE)
        result = local.diff(remote, "path")
        assert any("visibility" in c.path for c in result)

    def test_diff_visibility_same_no_change(self):
        local = _make_repo(visibility=RepositoryVisibility.PUBLIC)
        remote = _make_repo(visibility=RepositoryVisibility.PUBLIC)
        assert not any("visibility" in c.path for c in local.diff(remote, "path"))

class TestDiffRepositoryTopicsChanged:
    def test_diff_topic_added_in_local(self):
        local = _make_repo(topics=["python"])
        remote = _make_repo(topics=[])
        result = local.diff(remote, "path")
        topic_changes = [c for c in result if "topics" in c.path]
        assert len(topic_changes) == 1
        assert topic_changes[0].type == ChangeType.ADDED
        assert topic_changes[0].local == "python"

    def test_diff_topic_removed_from_local(self):
        local = _make_repo(topics=[])
        remote = _make_repo(topics=["python"])
        result = local.diff(remote, "path")
        topic_changes = [c for c in result if "topics" in c.path]
        assert topic_changes[0].type == ChangeType.REMOVED

    def test_diff_multiple_topics_added(self):
        local = _make_repo(topics=["a", "b", "c"])
        remote = _make_repo(topics=[])
        result = local.diff(remote, "path")
        topic_changes = [c for c in result if "topics" in c.path]
        assert len(topic_changes) == 3

    def test_diff_shared_topics_not_reported(self):
        local = _make_repo(topics=["shared", "local_only"])
        remote = _make_repo(topics=["shared", "remote_only"])
        result = local.diff(remote, "path")
        topic_vals = [c.local or c.remote for c in result if "topics" in c.path]
        assert "shared" not in topic_vals

    def test_diff_topics_same_no_change(self):
        local = _make_repo(topics=["python", "ml"])
        remote = _make_repo(topics=["ml", "python"])
        assert not any("topics" in c.path for c in local.diff(remote, "path"))

class TestDiffRepositoryPermissionsChanged:
    def _perms(self, **kwargs):
        defaults = dict(admin=[], maintain=[], write=[], triage=[], read=[])
        defaults.update(kwargs)
        return RepositoryPermissions(**defaults)

    def test_diff_permissions_both_none_no_change(self):
        local = _make_repo(permissions=None)
        remote = _make_repo(permissions=None)
        assert local.diff(remote, "path") == []

    def test_diff_permissions_added_local_has_remote_none(self):
        local = _make_repo(permissions=self._perms(admin=["alice"]))
        remote = _make_repo(permissions=None)
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.ADDED for c in result)

    def test_diff_permissions_removed_local_none_remote_has(self):
        local = _make_repo(permissions=None)
        remote = _make_repo(permissions=self._perms(admin=["alice"]))
        result = local.diff(remote, "path")
        assert any(c.type == ChangeType.REMOVED for c in result)

    def test_diff_permissions_admin_changed(self):
        local = _make_repo(permissions=self._perms(admin=["alice"]))
        remote = _make_repo(permissions=self._perms(admin=["bob"]))
        result = local.diff(remote, "path")
        assert len(result) == 2  # alice added, bob removed

class TestDiffRepositoryMultipleFields:
    def test_diff_description_and_topics_both_changed(self):
        local = _make_repo(description="new", topics=["python"])
        remote = _make_repo(description="old", topics=[])
        result = local.diff(remote, "path")
        assert any("description" in c.path for c in result)
        assert any("topics" in c.path for c in result)

    def test_diff_all_fields_identical_no_changes(self):
        r = _make_repo(
            description="d",
            archive=True,
            visibility=RepositoryVisibility.INTERNAL,
            topics=["a", "b"],
        )
        assert r.diff(r, "path") == []

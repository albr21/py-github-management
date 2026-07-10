from types import SimpleNamespace
from unittest.mock import Mock

from github_management.model.creation.repository.configuration import Configuration


class TestCreationConfigurationFromYaml:
    def test_creation_configuration_from_yaml_parses_yaml_string(self):
        yaml_str = "template_repository: org/template\nname: my-repo\ndescription: a repo\nprivate: true\n"

        config = Configuration.from_yaml(yaml_str)

        assert config.name == "my-repo"
        assert config.template_repository == "org/template"
        assert config.description == "a repo"
        assert config.private is True

class TestCreationConfigurationStr:
    def test_creation_configuration_str_returns_formatted_fields(self):
        config = Configuration(template_repository="org/template", name="my-repo")

        assert "Configuration(" in str(config)
        assert "name='my-repo'" in str(config)

class TestCreationConfigurationCreate:
    def test_creation_configuration_create_uses_template_and_applies_settings(self):
        branch_protection = Mock()
        pr_configuration = Mock()
        created_repository = SimpleNamespace(name="new-repo")
        created_repository.edit = Mock()

        class FakeUser:
            def __init__(self):
                self.calls = []

            def create_repo_from_template(self, **kwargs):
                self.calls.append(kwargs)
                return created_repository

        fake_user = FakeUser()
        fake_client = SimpleNamespace(
            client=SimpleNamespace(
                get_user=lambda: fake_user,
                get_repo=lambda name: SimpleNamespace(name=name),
            )
        )



        configuration = Configuration(
            template_repository="org/template",
            name="new-repo",
            description="desc",
            private=True,
            include_all_branches=True,
            branch_protection=branch_protection,
            pr_configuration=pr_configuration,
        )

        configuration.create(fake_client)

        assert fake_user.calls[0]["repo"].name == "org/template"
        assert fake_user.calls[0]["name"] == "new-repo"
        branch_protection.apply.assert_called_once_with(github_repository=created_repository)
        pr_configuration.apply.assert_called_once_with(github_repository=created_repository)

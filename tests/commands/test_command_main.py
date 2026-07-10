from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import github_management.main as main_module

class TestCommandMainDispatch:
    def test_command_main_validate_uses_validate_without_client(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="validate", file="/tmp/file.yaml")))
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "validate", Mock())
        monkeypatch.setattr(main_module, "Client", Mock(side_effect=AssertionError("Client should not be created")))

        main_module.main()

        main_module.validate.assert_called_once()

    def test_command_main_extract_uses_client_and_extract(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="extract", orgs=["OrgA"], file="/tmp/file.yaml")))
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "extract", Mock())
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        main_module.main()

        main_module.extract.assert_called_once()
        main_module.Client.assert_called_once()

    def test_command_main_diff_uses_client_and_diff(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="diff", orgs=["OrgA"], file="/tmp/file.yaml")))
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "diff", Mock())
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        main_module.main()

        main_module.diff.assert_called_once()

    def test_command_main_push_user_dispatches(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="push", push_scope="user", push_target="topics")))
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "push_user_parser", Mock())
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        main_module.main()

        main_module.push_user_parser.assert_called_once()

    def test_command_main_push_org_dispatches(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="push", push_scope="org", push_target="topics")))
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "push_org_parser", Mock())
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        main_module.main()

        main_module.push_org_parser.assert_called_once()

    def test_command_main_create_repo_dispatches(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="create", create_target="repo", file="/tmp/file.yaml", dry_run=False)))
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "create_repo", Mock())
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        main_module.main()

        main_module.create_repo.assert_called_once()

    def test_command_main_create_unknown_target_exits(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="create", create_target="bad", file="/tmp/file.yaml", dry_run=False)), print_help=Mock())
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        with pytest.raises(SystemExit):
            main_module.main()

        parser.print_help.assert_called_once()

    def test_command_main_push_unknown_scope_exits(self, monkeypatch):
        parser = SimpleNamespace(parse_args=Mock(return_value=SimpleNamespace(command="push", push_scope="bad")), print_help=Mock())
        monkeypatch.setattr(main_module, "build_cli", Mock(return_value=parser))
        monkeypatch.setattr(main_module, "Client", Mock(return_value=SimpleNamespace()))

        with pytest.raises(SystemExit):
            main_module.main()

        parser.print_help.assert_called_once()

class TestCommandMainPushParserHelpers:
    def test_command_push_user_parser_dispatches_to_topics(self, monkeypatch):
        topics_mock = Mock()
        monkeypatch.setattr(main_module, "push_user_topics", topics_mock)

        main_module.push_user_parser(SimpleNamespace(), SimpleNamespace(push_target="topics"))

        topics_mock.assert_called_once()

    def test_command_push_user_parser_unknown_target_exits(self):
        with pytest.raises(SystemExit):
            main_module.push_user_parser(SimpleNamespace(), SimpleNamespace(push_target="bad"))

    def test_command_push_org_parser_dispatches_to_topics(self, monkeypatch):
        topics_mock = Mock()
        monkeypatch.setattr(main_module, "push_org_topics", topics_mock)

        main_module.push_org_parser(SimpleNamespace(), SimpleNamespace(push_target="topics"))

        topics_mock.assert_called_once()

    def test_command_push_org_parser_unknown_target_exits(self):
        with pytest.raises(SystemExit):
            main_module.push_org_parser(SimpleNamespace(), SimpleNamespace(push_target="bad"))

    def test_command_push_user_parser_dispatches_to_cleanup(self, monkeypatch):
        cleanup_mock = Mock()
        monkeypatch.setattr(main_module, "push_user_cleanup", cleanup_mock)

        main_module.push_user_parser(SimpleNamespace(), SimpleNamespace(push_target="cleanup"))

        cleanup_mock.assert_called_once()

    def test_command_push_org_parser_dispatches_to_cleanup(self, monkeypatch):
        cleanup_mock = Mock()
        monkeypatch.setattr(main_module, "push_org_cleanup", cleanup_mock)

        main_module.push_org_parser(SimpleNamespace(), SimpleNamespace(push_target="cleanup"))

        cleanup_mock.assert_called_once()

    def test_command_push_org_parser_dispatches_to_teams(self, monkeypatch):
        teams_mock = Mock()
        monkeypatch.setattr(main_module, "push_org_teams", teams_mock)

        main_module.push_org_parser(SimpleNamespace(), SimpleNamespace(push_target="teams"))

        teams_mock.assert_called_once()

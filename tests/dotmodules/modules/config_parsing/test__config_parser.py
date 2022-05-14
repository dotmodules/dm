from pathlib import Path
from typing import Dict, List, cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules import (
    ConfigError,
    ConfigParser,
    LinkCleanUpHook,
    LinkDeploymentHook,
    Module,
    Modules,
    RawCommonConfigDataType,
    ShellScriptHook,
)


class TestStringParsing:
    def test__valid_string_can_be_parsed(self) -> None:
        dummy_value = "some value"
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {
            dummy_key: dummy_value,
        }
        result = ConfigParser._parse_string(data=dummy_data, key=dummy_key)
        assert result == dummy_value

    def test__missing_key__error_should_be_raised(self) -> None:
        dummy_key = "invalid_key"
        dummy_data: RawCommonConfigDataType = {}
        with pytest.raises(SyntaxError) as exception_info:
            ConfigParser._parse_string(data=dummy_data, key=dummy_key)
        expected = f"mandatory '{dummy_key}' section is missing"
        assert str(exception_info.value) == expected

    def test__missing_key__but_not_mandatory__empty_should_be_returned(self) -> None:
        dummy_key = "invalid_key"
        dummy_data: RawCommonConfigDataType = {}
        result = ConfigParser._parse_string(
            data=dummy_data, key=dummy_key, mandatory=False
        )
        assert result == ""

    def test__empty_value__error_should_be_raised(self) -> None:
        dummy_value = ""
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {
            dummy_key: dummy_value,
        }
        with pytest.raises(ValueError) as exception_info:
            ConfigParser._parse_string(data=dummy_data, key=dummy_key)
        expected = f"empty value for section '{dummy_key}'"
        assert str(exception_info.value) == expected

    def test__empty_value__but_not_mandatory__empty_should_be_returned(self) -> None:
        dummy_value = ""
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {
            dummy_key: dummy_value,
        }
        result = ConfigParser._parse_string(
            data=dummy_data, key=dummy_key, mandatory=False
        )
        assert result == ""

    def test__non_string_value__error_should_be_raised(self) -> None:
        dummy_value = ["this", "is", "not", "a", "string"]
        dummy_key = "key"
        dummy_data: Dict[str, List[str]] = {
            dummy_key: dummy_value,
        }
        with pytest.raises(ValueError) as exception_info:
            # This is an error case, typing will be ignored..
            ConfigParser._parse_string(data=dummy_data, key=dummy_key)  # type: ignore
        expected = f"value for section '{dummy_key}' should be a string"
        assert str(exception_info.value) == expected


class TestItemListParsing:
    def test__missing_key_should_be_converted_to_an_empty_list(
        self, mocker: MockerFixture
    ) -> None:
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {}
        mock_item_class = mocker.Mock()
        result = ConfigParser._parse_item_list(
            data=dummy_data, key=dummy_key, item_class=mock_item_class
        )
        mock_item_class.assert_not_called()
        assert result == []

    def test__none_value_should_be_converted_to_an_empty_list(
        self, mocker: MockerFixture
    ) -> None:
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {
            dummy_key: None,
        }
        mock_item_class = mocker.Mock()
        result = ConfigParser._parse_item_list(
            data=dummy_data, key=dummy_key, item_class=mock_item_class
        )
        mock_item_class.assert_not_called()
        assert result == []

    def test__items_get_initialized(self, mocker: MockerFixture) -> None:
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {
            dummy_key: [
                {
                    "field_1": "value_1",
                    "field_2": "value_2",
                },
            ]
        }
        mock_item_class = mocker.Mock()
        mock_item_object = mocker.Mock()
        mock_item_class.return_value = mock_item_object
        result = ConfigParser._parse_item_list(
            data=dummy_data, key=dummy_key, item_class=mock_item_class
        )
        mock_item_class.assert_called_with(field_1="value_1", field_2="value_2")
        assert result == [mock_item_object]

    def test__error_during_instantiation_means_syntax_error(
        self, mocker: MockerFixture
    ) -> None:
        dummy_key = "key"
        dummy_data: RawCommonConfigDataType = {
            dummy_key: [
                {
                    "field_1": "value_1",
                    "field_2": "value_2",
                },
            ]
        }
        mock_item_class = mocker.Mock()
        mock_item_class.side_effect = TypeError("some error")
        with pytest.raises(SyntaxError) as exception_info:
            ConfigParser._parse_item_list(
                data=dummy_data, key=dummy_key, item_class=mock_item_class
            )
        expected = "unexpected error happened while processing 'key' item at index '1': 'some error'"
        assert str(exception_info.value) == expected


class TestTopLevelStringBasedParsing:
    def test__name_can_be_parsed_as_a_string(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "name": "my name",
        }
        result = ConfigParser.parse_name(data=dummy_data)
        assert result == "my name"

    def test__version_can_be_parsed_as_a_string(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "version": "my version",
        }
        result = ConfigParser.parse_version(data=dummy_data)
        assert result == "my version"

    def test__documentation_can_be_parsed_as_a_list_of_lines__single_line(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "documentation": "line 1",
        }
        result = ConfigParser.parse_documentation(data=dummy_data)
        assert result == ["line 1"]

    def test__documentation_can_be_parsed_as_a_list_of_lines__multiline(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "documentation": "line 1\nline 2",
        }
        result = ConfigParser.parse_documentation(data=dummy_data)
        assert result == ["line 1", "line 2"]


class TestVariablesParsing:
    def test__missing_key_should_be_converted_to_dict(self) -> None:
        dummy_data: RawCommonConfigDataType = {}
        result = ConfigParser.parse_variables(data=dummy_data)
        assert result == {}

    def test__empty_value_should_be_left_as_is(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "variables": {},
        }
        result = ConfigParser.parse_variables(data=dummy_data)
        assert result == {}

    def test__scalar_value__error_should_be_raised(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "variables": "I am a string",
        }
        with pytest.raises(SyntaxError) as exception_info:
            ConfigParser.parse_variables(data=dummy_data)
        expected = "the 'variables' section should have the following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..]"
        assert str(exception_info.value) == expected

    def test__non_string_key__error_should_be_raised(self) -> None:
        dummy_data = {
            "variables": {
                42: ["non", "string", "key"],
            },
        }
        with pytest.raises(SyntaxError) as exception_info:
            # This is an error case, mypy cannot resolve this.
            ConfigParser.parse_variables(data=dummy_data)  # type: ignore
        expected = "the 'variables' section should only have string variable names"
        assert str(exception_info.value) == expected

    def test__non_compatible_variable__error_should_be_raised(self) -> None:
        dummy_data = {
            "variables": {
                "VARIABLE": {"this is not a list": 42},
            },
        }
        with pytest.raises(ValueError) as exception_info:
            # This is an error case, mypy cannot resolve this.
            ConfigParser.parse_variables(data=dummy_data)  # type: ignore
        expected = "the 'variables' section should contain a single string or a list of strings for a variable name"
        assert str(exception_info.value) == expected

    def test__non_list_variable_name__should_be_converted_to_a_list(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "variables": {
                "VARIABLE": "I am not a list",
            },
        }
        result = ConfigParser.parse_variables(data=dummy_data)
        assert result == {
            "VARIABLE": ["I am not a list"],
        }

    def test__non_string_items__error_should_be_raised(self) -> None:
        dummy_data = {
            "variables": {
                "VARIABLE": ["I am a string", 42],
            },
        }
        with pytest.raises(ValueError) as exception_info:
            # This is an error case, mypy cannot resolve this.
            ConfigParser.parse_variables(data=dummy_data)  # type: ignore
        expected = "the 'variables' section should contain a single string or a list of strings for a variable name"
        assert str(exception_info.value) == expected


class TestLinksParsing:
    def test__missing_key_should_be_converted_to_list(self) -> None:
        dummy_data: RawCommonConfigDataType = {}
        result = ConfigParser.parse_links(data=dummy_data)
        assert result == []

    def test__none_value_should_be_left_as_is(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "links": None,
        }
        result = ConfigParser.parse_links(data=dummy_data)
        assert result == []

    def test__empty_value_should_be_left_as_is(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "links": [],
        }
        result = ConfigParser.parse_links(data=dummy_data)
        assert result == []

    def test__valid_link_can_be_parsed(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "links": [
                {
                    "path_to_file": "my_path_to_file",
                    "path_to_symlink": "my_path_to_symlink",
                    "name": "my_name",
                },
            ],
        }
        result = ConfigParser.parse_links(data=dummy_data)
        assert len(result) == 1
        link = result[0]
        assert link.path_to_file == "my_path_to_file"
        assert link.path_to_symlink == "my_path_to_symlink"
        assert link.name == "my_name"

    def test__name_is_optional(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "links": [
                {
                    "path_to_file": "my_path_to_file",
                    "path_to_symlink": "my_path_to_symlink",
                },
            ],
        }
        result = ConfigParser.parse_links(data=dummy_data)
        assert len(result) == 1
        link = result[0]
        assert link.path_to_file == "my_path_to_file"
        assert link.path_to_symlink == "my_path_to_symlink"
        assert link.name == "link"

    def test__invalid_data__error_should_be_raised(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "links": [
                {
                    "invalid_key": "invalid_value",
                },
            ],
        }
        with pytest.raises(SyntaxError) as exception_info:
            ConfigParser.parse_links(data=dummy_data)
        expected_section_1 = (
            "unexpected error happened while processing 'links' item at index '1':"
        )
        expected_section_2 = "invalid_key"
        assert expected_section_1 in str(exception_info.value)
        assert expected_section_2 in str(exception_info.value)


class TestHooksParsing:
    def test__missing_key_should_be_converted_to_list(self) -> None:
        dummy_data: RawCommonConfigDataType = {}
        result = ConfigParser.parse_hooks(data=dummy_data)
        assert result == []

    def test__none_value_should_be_left_as_is(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "hooks": None,
        }
        result = ConfigParser.parse_hooks(data=dummy_data)
        assert result == []

    def test__empty_value_should_be_left_as_is(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "hooks": [],
        }
        result = ConfigParser.parse_hooks(data=dummy_data)
        assert result == []

    def test__valid_hook_can_be_parsed(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "hooks": [
                {
                    "name": "my_hook_name",
                    "path_to_script": "my_path_to_script",
                    "priority": 42,
                },
            ],
        }
        result = ConfigParser.parse_hooks(data=dummy_data)
        assert len(result) == 1
        hook = result[0]
        assert hook.path_to_script == "my_path_to_script"
        assert hook.name == "my_hook_name"
        assert hook.priority == 42

    def test__priority_is_optional(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "hooks": [
                {
                    "name": "my_hook_name",
                    "path_to_script": "my_path_to_script",
                },
            ],
        }
        result = ConfigParser.parse_hooks(data=dummy_data)
        assert len(result) == 1
        hook = result[0]
        assert hook.path_to_script == "my_path_to_script"
        assert hook.name == "my_hook_name"
        assert hook.priority == 0

    def test__invalid_data__error_should_be_raised(self) -> None:
        dummy_data: RawCommonConfigDataType = {
            "hooks": [
                {
                    "invalid_key": "invalid_value",
                },
            ],
        }
        with pytest.raises(SyntaxError) as exception_info:
            ConfigParser.parse_hooks(data=dummy_data)
        expected_section_1 = (
            "unexpected error happened while processing 'hooks' item at index '1':"
        )
        expected_section_2 = "invalid_key"
        assert expected_section_1 in str(exception_info.value)
        assert expected_section_2 in str(exception_info.value)


@pytest.mark.integration
class TestEndToEndConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "sample_config_files"

    def test__valid_file__full(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "valid__full.toml"
        module = Module.from_path(path=file_path)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == [
            "line 1",
            " line 2",
            "  line 3",
        ]
        assert module.variables == {
            "VAR_1": ["var1"],
            "VAR_2": ["var21", "var22", "var23"],
        }

        assert len(module.links) == 2

        link = module.links[0]
        assert link.name == "link_name_1"
        assert link.path_to_file == "path_to_file_1"
        assert link.path_to_symlink == "path_to_symlink_1"

        link = module.links[1]
        assert link.name == "link_name_2"
        assert link.path_to_file == "path_to_file_2"
        assert link.path_to_symlink == "path_to_symlink_2"

        assert len(module.hooks) == 2

        hook = cast(ShellScriptHook, module.hooks[0])
        assert hook.name == "hook_name_1"
        assert hook.path_to_script == "path_to_script_1"
        assert hook.priority == 1

        hook = cast(ShellScriptHook, module.hooks[1])
        assert hook.name == "hook_name_2"
        assert hook.path_to_script == "path_to_script_2"
        assert hook.priority == 2

    def test__valid_file__minimal(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "valid__minimal.toml"
        module = Module.from_path(path=file_path)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []

    def test__invalid_file__non_existent_file(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "NON_EXISTENT"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected_section_1 = (
            "configuration loading error: [Errno 2] No such file or directory:"
        )
        expected_section_2 = "NON_EXISTENT"
        assert expected_section_1 in str(exception_info.value)
        assert expected_section_2 in str(exception_info.value)

    def test__invalid_file__toml_syntax(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__toml_syntax.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = "configuration loading error: Found tokens after a closed string. Invalid TOML. (line 1 column 1 char 0)"
        assert str(exception_info.value) == expected

    def test__invalid_file__name_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__name_missing.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = "configuration syntax error: mandatory 'name' section is missing"
        assert str(exception_info.value) == expected

    def test__invalid_file__name_empty(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__name_empty.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = "configuration value error: empty value for section 'name'"
        assert str(exception_info.value) == expected

    def test__invalid_file__name_non_string(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__name_non_string.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "configuration value error: value for section 'name' should be a string"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__version_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__version_missing.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = "configuration syntax error: mandatory 'version' section is missing"
        assert str(exception_info.value) == expected

    def test__invalid_file__version_empty(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__version_empty.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = "configuration value error: empty value for section 'version'"
        assert str(exception_info.value) == expected

    def test__invalid_file__version_non_string(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__version_non_string.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "configuration value error: value for section 'version' should be a string"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__variables_structure(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__variables_structure.toml"
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "configuration syntax error: the 'variables' section should have the "
            "following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..]"
        )
        assert str(exception_info.value) == expected

    def test__unexpected_error_can_be_handled(self, mocker: MockerFixture) -> None:
        file_path = self.SAMPLE_FILE_DIR / "irrelevant_file.toml"
        mocker.patch("dotmodules.modules.ConfigLoader.load_raw_config_data")
        mocker.patch(
            "dotmodules.modules.ConfigParser.parse_name",
            side_effect=Exception("shit happens"),
        )
        with pytest.raises(ConfigError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "unexpected error happened during configuration parsing: shit happens"
        )
        assert str(exception_info.value) == expected


@pytest.mark.integration
class TestEndToEndModuleLoadingCases:
    def test__modules_can_be_loaded_from_a_directory_structure(self) -> None:
        modules_root_path = Path(__file__).parent / "dummy_modules_dir"
        config_file_name = "config.toml"
        modules = Modules.load(
            modules_root_path=modules_root_path, config_file_name=config_file_name
        )
        assert modules
        assert len(modules) == 3

        # Modules are sorted by root:
        # .../category_1/module_2
        # .../category_1/module_3
        # .../module_1

        # =====================================================================
        module = modules.modules[0]
        assert isinstance(module, Module)
        assert module.name == "module_2"
        assert module.version == "version_2"
        assert module.documentation == ["docs_2"]
        assert module.variables == {
            "VAR_2_1": ["var_1"],
            "VAR_2_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_2"
        assert link.path_to_file == "path_to_file_2"
        assert link.path_to_symlink == "path_to_symlink_2"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
        assert hook.get_name() == "hook_name_2"
        assert hook.get_priority() == 2
        assert hook.get_details() == "path_to_script_2"
        assert hook.get_module_name() == "module_2"

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.get_name() == "DEPLOY_LINKS"
        assert hook.get_priority() == 0
        assert hook.get_details() == "Deploy 1 link"
        assert hook.get_module_name() == "module_2"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.get_name() == "CLEAN_UP_LINKS"
        assert hook.get_priority() == 0
        assert hook.get_details() == "Clean up 1 link"
        assert hook.get_module_name() == "module_2"
        assert hook.links == module.links

        # =====================================================================
        # MODULE 2
        module = modules.modules[1]
        assert isinstance(module, Module)
        assert module.name == "module_3"
        assert module.version == "version_3"
        assert module.documentation == ["docs_3"]
        assert module.variables == {
            "VAR_3_1": ["var_1"],
            "VAR_3_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_3"
        assert link.path_to_file == "path_to_file_3"
        assert link.path_to_symlink == "path_to_symlink_3"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
        assert hook.get_name() == "hook_name_3"
        assert hook.get_priority() == 3
        assert hook.get_details() == "path_to_script_3"
        assert hook.get_module_name() == "module_3"

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.get_name() == "DEPLOY_LINKS"
        assert hook.get_priority() == 0
        assert hook.get_details() == "Deploy 1 link"
        assert hook.get_module_name() == "module_3"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.get_name() == "CLEAN_UP_LINKS"
        assert hook.get_priority() == 0
        assert hook.get_details() == "Clean up 1 link"
        assert hook.get_module_name() == "module_3"
        assert hook.links == module.links

        # =====================================================================
        module = modules.modules[2]
        assert isinstance(module, Module)
        assert module.name == "module_1"
        assert module.version == "version_1"
        assert module.documentation == ["docs_1"]
        assert module.variables == {
            "VAR_1_1": ["var_1"],
            "VAR_1_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_1"
        assert link.path_to_file == "path_to_file_1"
        assert link.path_to_symlink == "path_to_symlink_1"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
        assert hook.get_name() == "hook_name_1"
        assert hook.get_priority() == 1
        assert hook.get_details() == "path_to_script_1"
        assert hook.get_module_name() == "module_1"

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.get_name() == "DEPLOY_LINKS"
        assert hook.get_priority() == 0
        assert hook.get_details() == "Deploy 1 link"
        assert hook.get_module_name() == "module_1"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.get_name() == "CLEAN_UP_LINKS"
        assert hook.get_priority() == 0
        assert hook.get_details() == "Clean up 1 link"
        assert hook.get_module_name() == "module_1"
        assert hook.links == module.links

    def test__error_during_loading(self) -> None:
        modules_root_path = Path(__file__).parent / "dummy_modules_dir_error"
        config_file_name = "config.toml"
        with pytest.raises(ConfigError) as exception_info:
            Modules.load(
                modules_root_path=modules_root_path, config_file_name=config_file_name
            )
        expected = "got an unexpected keyword argument 'INVALID'"
        assert expected in str(exception_info.value)

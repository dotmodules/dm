from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.modules import Module, ModuleError


@pytest.mark.integration
class TestInvalidGeneralConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__non_existent_file(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "NON_EXISTENT"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            f"Configuration loading error: Config file at path '{file_path}' does "
            "not exist!"
        )
        assert exception_info.match(expected)

    def test__toml_syntax(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_toml_syntax.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Configuration loading error: Toml loading error: .*"
        assert exception_info.match(expected)

    def test__unexpected_error_can_be_handled(self, mocker: MockerFixture) -> None:
        file_path = self.SAMPLE_FILE_DIR / "irrelevant_file.toml"
        mocker.patch(
            "dotmodules.modules.loader.ConfigLoader.get_loader_for_config_file"
        )
        mocker.patch(
            "dotmodules.modules.parser.ConfigParser.parse_name",
            side_effect=Exception("shit happens"),
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Unexpected error happened during module loading: shit happens"
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidNameConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "name"

    def test__name_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "name_missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Configuration syntax error: Mandatory 'name' section is missing!"
        assert exception_info.match(expected)

    def test__name_empty(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "name_empty.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Configuration syntax error: Empty value for section 'name'!"
        assert exception_info.match(expected)

    def test__name_non_string(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "name_non_string.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Value for section 'name' should be a string, "
            "got list!"
        )
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidVersionConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "version"

    def test__version_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "version_missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Configuration syntax error: Mandatory 'version' section is missing!"
        assert exception_info.match(expected)

    def test__version_empty(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "version_empty.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Configuration syntax error: Empty value for section 'version'!"
        assert exception_info.match(expected)

    def test__version_non_string(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "version_non_string.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Value for section 'version' "
            "should be a string, got list!"
        )
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidEnabledConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "enabled"

    def test__global_enabled__non_boolean(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "global__non_boolean.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: The value for section 'enabled' should "
            "be boolean, got str!"
        )
        assert exception_info.match(expected)

    def test__global_enabled_missing__without_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "global__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = "Configuration syntax error: Mandatory section 'enabled' is missing!"
        assert exception_info.match(expected)

    def test__global_enabled_missing__with_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "global__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="my_target")
        expected = "Configuration syntax error: Mandatory section 'enabled' is missing!"
        assert exception_info.match(expected)

    def test__missing_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="my_target")
        expected = (
            "Configuration syntax error: Missing deployment target 'my_target' from "
            "section 'enabled'!"
        )
        assert exception_info.match(expected)

    def test__deployment_target_is_not_a_boolean(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target__non_boolean.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="my_target")
        expected = (
            "Configuration syntax error: The value for section 'enabled' should be "
            "boolean for deployment target 'my_target', got int!"
        )
        assert exception_info.match(expected)

    def test__separated_enabled_field__but_deployment_target_is_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Section 'enabled' was defined for deployment "
            "targets only, but there is no deployment target specified for the current deployment!"
        )
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidDocumentationConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "documentation"

    def test__invalid_documentation_type(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_documentation_type.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Value for section 'documentation' should be "
            "a string, got int!"
        )
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidVariablesConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "variables"

    def test__invalid_variables_structure(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_variables_structure.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: The 'variables' section should have the "
            r"following syntax: 'VARIABLE_NAME' = \['var_1', 'var_2', ..\] !"
        )
        assert exception_info.match(expected)

    def test__invalid_variable_value_1(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_variable_value_1.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: The 'variables' section should contain a "
            "single string or a list of strings for a variable name!"
        )
        assert exception_info.match(expected)

    def test__invalid_variable_value_2(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_variable_value_2.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: The 'variables' section should contain a "
            "single string or a list of strings for a variable name!"
        )
        assert exception_info.match(expected)

    def test__deployment_target_redefines_variable_name(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target_redefines_variable.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="my_target")
        expected = (
            "Configuration syntax error: Deployment target specific variable section "
            "'variables__my_target' redefined already existing global variable key 'VAR_1'!"
        )
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidLinksConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "links"

    def test__links_missing_mandatory_field_1(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_missing_mandatory_field_1.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Missing mandatory field 'name' from section 'links' "
            "item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_missing_mandatory_field_2(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_missing_mandatory_field_2.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_target' from section "
            "'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_missing_mandatory_field_3(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_missing_mandatory_field_3.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_symlink' from section "
            "'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_additional_field(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_additional_field.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Unexpected field 'additional_field' found for section "
            "'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_additional_fields(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_additional_fields.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Unexpected fields 'additional_field_1', "
            "'additional_field_2' found for section 'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__invalid_value_type(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_value_type.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: The value for field 'name' should be an "
            "str in section 'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__item_type_is_not_a_list_of_objects(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "item_type_is_not_a_list_of_objects.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Invalid value for 'links'! It should contain "
            "a list of objects!"
        )
        assert exception_info.match(expected)

    def test__not_a_list(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "not_a_list.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Invalid value for 'links'! It should contain "
            "a list of objects!"
        )
        assert exception_info.match(expected)

    def test__deployment_target_redefines_link(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target_redefines_link.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="my_target")
        expected = (
            "Configuration syntax error: Deployment target specific link section 'links__my_target' "
            "contains an already defined link item!"
        )
        assert exception_info.match(expected)


@pytest.mark.integration
class TestInvalidHooksConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "hooks"

    def test__hooks_missing_mandatory_field_1(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_missing_mandatory_field_1.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Missing mandatory field 'name' from section 'hooks' "
            "item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_missing_mandatory_field_2(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_missing_mandatory_field_2.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_script' from section "
            "'hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_missing_mandatory_field_3(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_missing_mandatory_field_3.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Missing mandatory field 'priority' from section "
            "'hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_additional_field(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_additional_field.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Unexpected field 'additional_field' found for section "
            "'hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_additional_fields(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_additional_fields.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Unexpected fields 'additional_field_1', "
            "'additional_field_2' found for section 'hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__invalid_value_type(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_value_type.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: The value for field 'name' should be an str "
            "in section 'hooks' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__item_type_is_not_a_list_of_objects(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "item_type_is_not_a_list_of_objects.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Invalid value for 'hooks'! It should contain "
            "a list of objects!"
        )
        assert exception_info.match(expected)

    def test__not_a_list(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "not_a_list.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="")
        expected = (
            "Configuration syntax error: Invalid value for 'hooks'! It should contain "
            "a list of objects!"
        )
        assert exception_info.match(expected)

    def test__deployment_arget_redefines_hook(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target_redefines_hook.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="my_target")
        expected = (
            "Configuration syntax error: Deployment target specific hook section 'hooks__my_target' "
            "contains an already defined hook item!"
        )
        assert exception_info.match(expected)

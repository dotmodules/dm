from pathlib import Path
from typing import cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.modules import Module, ModuleError, Modules


@pytest.fixture
def modules(mocker: MockerFixture) -> Modules:
    mock_modules = mocker.MagicMock()
    return cast(Modules, mock_modules)


@pytest.mark.integration
class TestInvalidShellScriptHooksConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__hooks_missing_mandatory_field_1(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_missing_mandatory_field_1.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Missing mandatory field 'name' from section "
            "'shell_script_hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_missing_mandatory_field_2(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_missing_mandatory_field_2.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_script' from section "
            "'shell_script_hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_missing_mandatory_field_3(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_missing_mandatory_field_3.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Missing mandatory field 'priority' from section "
            "'shell_script_hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_additional_field(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_additional_field.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Unexpected field 'additional_field' found for "
            "section 'shell_script_hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__hooks_additional_fields(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "hook_additional_fields.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Unexpected fields 'additional_field_1', "
            "'additional_field_2' found for section 'shell_script_hooks' item at index 2!"
        )
        assert exception_info.match(expected)

    def test__invalid_value_type(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_value_type.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: The value for field 'name' should be an str "
            "in section 'shell_script_hooks' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__item_type_is_not_a_list_of_objects(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "item_type_is_not_a_list_of_objects.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Invalid value for 'shell_script_hooks'! It should "
            "contain a list of objects!"
        )
        assert exception_info.match(expected)

    def test__not_a_list(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "not_a_list.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Invalid value for 'shell_script_hooks'! It should "
            "contain a list of objects!"
        )
        assert exception_info.match(expected)

    def test__deployment_arget_redefines_hook(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target_redefines_hook.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(
                path=file_path, deployment_target="my_target", modules=modules
            )
        expected = (
            "Configuration syntax error: Deployment target specific hook section "
            "'shell_script_hooks__my_target' contains an already defined hook item!"
        )
        assert exception_info.match(expected)

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
class TestInvalidLinksConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__links_missing_mandatory_field_1(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_missing_mandatory_field_1.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Missing mandatory field 'name' from section 'links' "
            "item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_missing_mandatory_field_2(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_missing_mandatory_field_2.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_target' from section "
            "'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_missing_mandatory_field_3(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_missing_mandatory_field_3.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_symlink' from section "
            "'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_additional_field(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_additional_field.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Unexpected field 'additional_field' found for section "
            "'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__links_additional_fields(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "link_additional_fields.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Unexpected fields 'additional_field_1', "
            "'additional_field_2' found for section 'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__invalid_value_type(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_value_type.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: The value for field 'name' should be an "
            "str in section 'links' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__item_type_is_not_a_list_of_objects(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "item_type_is_not_a_list_of_objects.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Invalid value for 'links'! It should contain "
            "a list of objects!"
        )
        assert exception_info.match(expected)

    def test__not_a_list(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "not_a_list.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Invalid value for 'links'! It should contain "
            "a list of objects!"
        )
        assert exception_info.match(expected)

    def test__deployment_target_redefines_link(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target_redefines_link.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(
                path=file_path, deployment_target="my_target", modules=modules
            )
        expected = (
            "Configuration syntax error: Deployment target specific link section 'links__my_target' "
            "contains an already defined link item!"
        )
        assert exception_info.match(expected)

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
class TestInvalidVariablesConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__invalid_variables_structure(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_variables_structure.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: The 'variables' section should have the "
            r"following syntax: 'VARIABLE_NAME' = \['var_1', 'var_2', ..\] !"
        )
        assert exception_info.match(expected)

    def test__invalid_variable_value_1(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_variable_value_1.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: The 'variables' section should contain a "
            "single string or a list of strings for a variable name!"
        )
        assert exception_info.match(expected)

    def test__invalid_variable_value_2(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_variable_value_2.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: The 'variables' section should contain a "
            "single string or a list of strings for a variable name!"
        )
        assert exception_info.match(expected)

    def test__deployment_target_redefines_variable_name(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target_redefines_variable.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(
                path=file_path, deployment_target="my_target", modules=modules
            )
        expected = (
            "Configuration syntax error: Deployment target specific variable section "
            "'variables__my_target' redefined already existing global variable key 'VAR_1'!"
        )
        assert exception_info.match(expected)

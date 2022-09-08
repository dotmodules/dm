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
class TestInvalidEnabledConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__global_enabled__non_boolean(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "global__non_boolean.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: The value for section 'enabled' should "
            "be boolean, got str!"
        )
        assert exception_info.match(expected)

    def test__global_enabled_missing__without_deployment_target(
        self, modules: Modules
    ) -> None:
        file_path = self.SAMPLE_FILE_DIR / "global__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = "Configuration syntax error: Mandatory section 'enabled' is missing!"
        assert exception_info.match(expected)

    def test__global_enabled_missing__with_deployment_target(
        self, modules: Modules
    ) -> None:
        file_path = self.SAMPLE_FILE_DIR / "global__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(
                path=file_path, deployment_target="my_target", modules=modules
            )
        expected = "Configuration syntax error: Mandatory section 'enabled' is missing!"
        assert exception_info.match(expected)

    def test__missing_deployment_target(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(
                path=file_path, deployment_target="my_target", modules=modules
            )
        expected = (
            "Configuration syntax error: Missing deployment target 'my_target' from "
            "section 'enabled'!"
        )
        assert exception_info.match(expected)

    def test__deployment_target_is_not_a_boolean(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target__non_boolean.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(
                path=file_path, deployment_target="my_target", modules=modules
            )
        expected = (
            "Configuration syntax error: The value for section 'enabled' should be "
            "boolean for deployment target 'my_target', got int!"
        )
        assert exception_info.match(expected)

    def test__separated_enabled_field__but_deployment_target_is_missing(
        self, modules: Modules
    ) -> None:
        file_path = self.SAMPLE_FILE_DIR / "deployment_target__missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Section 'enabled' was defined for deployment "
            "targets only, but there is no deployment target specified for the current deployment!"
        )
        assert exception_info.match(expected)

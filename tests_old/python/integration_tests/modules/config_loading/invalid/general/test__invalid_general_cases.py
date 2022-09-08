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
class TestInvalidGeneralConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__non_existent_file(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "NON_EXISTENT"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            f"Configuration loading error: Config file at path '{file_path}' does "
            "not exist!"
        )
        assert exception_info.match(expected)

    def test__toml_syntax(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_toml_syntax.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = "Configuration loading error: Toml loading error: .*"
        assert exception_info.match(expected)

    def test__unexpected_error_can_be_handled(
        self, mocker: MockerFixture, modules: Modules
    ) -> None:
        file_path = self.SAMPLE_FILE_DIR / "irrelevant_file.toml"
        mocker.patch(
            "dotmodules.modules.loader.ConfigLoader.get_loader_for_config_file"
        )
        mocker.patch(
            "dotmodules.modules.parser.ConfigParser.parse_name",
            side_effect=Exception("shit happens"),
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = "Unexpected error happened during module loading: shit happens"
        assert exception_info.match(expected)
